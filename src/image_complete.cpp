// include various packages
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <limits.h>
#include <sstream>
#include <assert.h>
// import opencv
#include <opencv2/opencv.hpp>

#include <iostream>
#include <vector>
#include <unordered_map>

// finding maximum and minimum given two different values, done using ternary operator
#ifndef MAX
#define MAX(a, b) ((a)>(b)?(a):(b))
#define MIN(a, b) ((a)<(b)?(a):(b))
#endif

#define _DEBUG

using namespace cv;
using namespace std;

// class for matrix of dots
class BITMAP { public:
  int w, h;
  int *data;
  BITMAP(int w_, int h_) :w(w_), h(h_) { data = new int[w*h]; }
  BITMAP(BITMAP* bm) {
    w = bm->w;
    h = bm->h;
    data = new int[w*h];
    for (int i = 0; i < w*h; ++i) {
        data[i] = bm->data[i];
    }
  }
  ~BITMAP() { delete[] data; }
  int *operator[](int y) { return &data[y*w]; }
};
// bounding box creation
struct Box {
  int xmin, xmax, ymin, ymax;
};

// initialize constraint map
struct CMap {
  unordered_map<int, vector<pair<int, int> > > constraint_map;
  vector<int> constraint_ids;
};

void getCMap(Mat constraint, CMap* cmap) {
  unordered_map<int, vector<pair<int, int> > >::iterator got;
  // traverse the image map within the constraints
  for (int y = 0; y < constraint.rows; ++y) {
    for (int x = 0; x < constraint.cols; ++x) {
      int cons_pixel = (int) constraint.at<uchar>(y, x);
      // check if pixel value is 0 
      if (cons_pixel == 0)
          continue;
      got = cmap->constraint_map.find(cons_pixel);
      if (got == cmap->constraint_map.end()) {
        vector<pair<int, int> > constraint_vector;
        // push the x and y value into vector if satisfied
        constraint_vector.push_back(make_pair(x, y));
        cmap->constraint_map[cons_pixel] = constraint_vector;
        cmap->constraint_ids.push_back(cons_pixel);
      } else {
        got->second.push_back(make_pair(x, y));
      }
    }
  }

  // print statements: rows and columns

  cout << "Rows: " << constraint.rows << ", Cols: " << constraint.cols << endl;
  cout << constraint.rows * constraint.cols << endl;


  cout << "Map has size of " << cmap->constraint_map.size() << endl;
  for (int i = 0; i < cmap->constraint_ids.size(); ++i) {
    int id = cmap->constraint_ids[i];
    cout << "  Map id " << id << " has " << cmap->constraint_map.find(id)->second.size() << " elements " <<endl;
  }

}


// set constant variables for patch match
int patch_w  = 8;
//patch match iterations
int pm_iters = 5;
int rs_max   = INT_MAX; 
int sigma = 1 * patch_w * patch_w;

#define XY_TO_INT(x, y) (((y)<<12)|(x))
#define INT_TO_X(v) ((v)&((1<<12)-1))
#define INT_TO_Y(v) ((v)>>12)

/* Get the bounding box of hole */
Box getBox(Mat mask) {
  // initialize min and max values for x and y
  int xmin = INT_MAX, ymin = INT_MAX;
  int xmax = 0, ymax = 0;
  // traverse the bounding box(mask taken from input)
  for (int h = 0; h < mask.rows; h++) {
    for (int w = 0; w < mask.cols; w++) {
      int mask_pixel = (int) mask.at<uchar>(h, w);
      // check if value is white
      if (mask_pixel == 255) {
          if (h < ymin)
            ymin = h;
          if (h > ymax)
            ymax = h;
          if (w < xmin)
            xmin = w;
          if (w > xmax)
            xmax = w;
      } else if (mask_pixel != 0) {
          cout << "Unfortunate!, value " << mask_pixel << " in pos x " << w << " , y" << h << endl;
      }
    }
  }
  xmin = xmin - patch_w + 1;
  ymin = ymin - patch_w + 1;
  // ternary operator. give value of xmin and ymin to 0 if xmin and ymin and is negative, after removing the patch size
  xmin = (xmin < 0) ? 0 : xmin;
  ymin = (ymin < 0) ? 0 : ymin;

  xmax = (xmax > mask.cols - patch_w + 1) ? mask.cols - patch_w +1 : xmax;
  ymax = (ymax > mask.rows - patch_w + 1) ? mask.rows - patch_w +1 : ymax;

  // print out values of bounding box
  printf("Hole's bounding box is x (%d, %d), y (%d, %d)\n", xmin, xmax, ymin, ymax);
  Box box = {xmin, xmax, ymin, ymax};
  return box;
}

// function to verify if a certain pixel is within the given bounding box under consideration
bool inBox(int x, int y, Box box) {
  // check condition, return true if within the bounding box
  if (x >= box.xmin && x <= box.xmax && y >= box.ymin && y <= box.ymax) {
    return true;
  }
  return false;
}


/* Measure distance between 2 patches with upper left corners (ax, ay) and (bx, by), terminating early if we exceed a cutoff distance.*/

int dist(Mat a, Mat b, int ax, int ay, int bx, int by, int cutoff=INT_MAX) {
  int ans = 0;
  if (a.type() != CV_8UC3) {
    cout << "Bad things happened in dist " <<endl;
    exit(1);
  }
  for (int dy = 0; dy < patch_w; dy++) {
    for (int dx = 0; dx < patch_w; dx++) {
      Vec3b ac = a.at<Vec3b>(ay + dy, ax + dx);
      Vec3b bc = b.at<Vec3b>(by + dy, bx + dx);

      int db = ac[0] - bc[0];
      int dg = ac[1] - bc[1];
      int dr = ac[2] - bc[2];
      ans += dr*dr + dg*dg + db*db;
    }
    if (ans >= cutoff) { return cutoff; }
  }
  if (ans < 0) return INT_MAX;
  return ans;
}

/*
PROPAGATION STEP HOLE FILLING
*/
void improve_guess(Mat a, Mat b, int ax, int ay, int &xbest, int &ybest, int &dbest, int bx, int by, int type) {
  int d = dist(a, b, ax, ay, bx, by, dbest);
  if ((d < dbest) && (ax != bx || ay != by) ) {
#ifdef DEBUG
      if (type == 0)
        printf("  Prop x: improve (%d, %d) old nn (%d, %d) new nn (%d, %d) old dist %d, new dist %d\n", ax, ay, xbest, ybest, bx, by, dbest, d);
      else if (type == 1)
        printf("  Prop y: improve (%d, %d) old nn (%d, %d) new nn (%d, %d) old dist %d, new dist %d\n", ax, ay, xbest, ybest, bx, by, dbest, d);
      else
        printf("  Random: improve (%d, %d) old nn (%d, %d) new nn (%d, %d) old dist %d, new dist %d\n", ax, ay, xbest, ybest, bx, by, dbest, d);
#endif
    dbest = d;
    xbest = bx;
    ybest = by;
  }
}

/* patchmatch with hole */
void patchmatch(Mat a, Mat b, BITMAP *&ann, BITMAP *&annd, Mat dilated_mask, Mat constraint, CMap* cmap) {
  /* Initialize with random nearest neighbor field (NNF). */
  ann = new BITMAP(a.cols, a.rows);
  annd = new BITMAP(a.cols, a.rows);
  int aew = a.cols - patch_w + 1, aeh = a.rows - patch_w + 1;
  int bew = b.cols - patch_w + 1, beh = b.rows - patch_w + 1;
  memset(ann->data, 0, sizeof(int) * a.cols * a.rows);
  memset(annd->data, 0, sizeof(int) * a.cols * a.rows);

  int bx, by;
  unordered_map<int, vector<pair<int, int> > >::iterator got;
  for (int ay = 0; ay < aeh; ay++) {
    for (int ax = 0; ax < aew; ax++) {
      bool valid = false;
      int const_pixel = (int) constraint.at<uchar>(ay, ax);

      // if not having constraint
      if (const_pixel == 0) {
        while (!valid) {
          bx = rand() % bew;
          by = rand() % beh;
          int mask_pixel = (int) dilated_mask.at<uchar>(by, bx);
          // should find patches outside the hole
          if (mask_pixel == 255) {
            valid = false;
          } else {
            valid = true;
          }
        }
      } else {
        got = cmap->constraint_map.find(const_pixel);
        if (got == cmap->constraint_map.end()) {
          cout << "Something wrong in constraint map " << endl;
          exit(1);
        }
        while (!valid) {
          int rand_index = rand() % got->second.size();
          bx = got->second[rand_index].first;
          by = got->second[rand_index].second;
          int mask_pixel = (int) dilated_mask.at<uchar>(by, bx);
          if (bx >= bew || by >= beh) {
              valid = false;
          } else if (mask_pixel == 255) {
            valid = false;
          } else {
            valid = true;
          }
        }
      }
      (*ann)[ay][ax] = XY_TO_INT(bx, by);
      (*annd)[ay][ax] = dist(a, b, ax, ay, bx, by);
    }
  }

#ifdef DEBUG
  for (int ay = 0; ay < aeh; ay++ ) {
    for (int ax = 0; ax < aew; ax++) {
      int vp = (*ann)[ay][ax];
      int xp = INT_TO_X(vp);
      int yp = INT_TO_Y(vp);
      int mask_pixel = (int) dilated_mask.at<uchar>(yp, xp);
      if (mask_pixel == 255) {
         cout << "Something wrong after init  " << xp << " ,  " << yp << " pixel " << mask_pixel << endl;
      }
    }
  }
#endif

  for (int iter = 0; iter < pm_iters; iter++) {
    int ystart = 0, yend = aeh, ychange = 1;
    int xstart = 0, xend = aew, xchange = 1;
    if (iter % 2 == 1) {
      xstart = xend-1; xend = -1; xchange = -1;
      ystart = yend-1; yend = -1; ychange = -1;
    }
    for (int ay = ystart; ay != yend; ay += ychange) {
      for (int ax = xstart; ax != xend; ax += xchange) {

        int const_pixel = (int) constraint.at<uchar>(ay, ax);

        /* Current (best) guess. */
        int v = (*ann)[ay][ax];
        int xbest = INT_TO_X(v), ybest = INT_TO_Y(v);
        int dbest = (*annd)[ay][ax];

        /* PROPAGATION STEP */
        if ((unsigned) (ax - xchange) < (unsigned) aew) {
          int vp = (*ann)[ay][ax-xchange];
          int xp = INT_TO_X(vp) + xchange, yp = INT_TO_Y(vp);

          if (((unsigned) xp < (unsigned) aew)) {
            int mask_pixel = (int) dilated_mask.at<uchar>(yp, xp);
            if (mask_pixel != 255) {
              int new_const_pixel = (int) constraint.at<uchar>(yp, xp);
              if (const_pixel == 0) {
                improve_guess(a, b, ax, ay, xbest, ybest, dbest, xp, yp, 0);
              } else if (const_pixel == new_const_pixel) {
                improve_guess(a, b, ax, ay, xbest, ybest, dbest, xp, yp, 0);
              }
            }
          }
        }

        if ((unsigned) (ay - ychange) < (unsigned) aeh) {
          int vp = (*ann)[ay-ychange][ax];
          int xp = INT_TO_X(vp), yp = INT_TO_Y(vp) + ychange;

          if (((unsigned) yp < (unsigned) aeh)) {
            int mask_pixel = (int) dilated_mask.at<uchar>(yp, xp);
            if (mask_pixel != 255) {
              int new_const_pixel = (int) constraint.at<uchar>(yp, xp);
              if (const_pixel == 0) {
                improve_guess(a, b, ax, ay, xbest, ybest, dbest, xp, yp, 1);
              } else if (const_pixel == new_const_pixel) {
                improve_guess(a, b, ax, ay, xbest, ybest, dbest, xp, yp, 1);
              }
            }
          }
        }

        /* RANDOM SEARCH */
        if (const_pixel == 0) {
          int rs_start = rs_max;
          if (rs_start > MAX(b.cols, b.rows)) { rs_start = MAX(b.cols, b.rows); }
          for (int mag = rs_start; mag >= 1; mag /= 2) {
            /* Sampling window */
            int xmin = MAX(xbest-mag, 0), xmax = MIN(xbest+mag+1, bew);
            int ymin = MAX(ybest-mag, 0), ymax = MIN(ybest+mag+1, beh);
            bool do_improve = false;
            do {
              int xp = xmin + rand() % (xmax-xmin);
              int yp = ymin + rand() % (ymax-ymin);
              int mask_pixel = (int) dilated_mask.at<uchar>(yp, xp);
              if (mask_pixel != 255) {
                improve_guess(a, b, ax, ay, xbest, ybest, dbest, xp, yp, 2);
                do_improve = true;
              }
            } while (!do_improve);
          }
        } else {
          got = cmap->constraint_map.find(const_pixel);
          int improve_times = (int) ceil(sqrt(got->second.size()));
          for (int i_t = 0; i_t < improve_times; ++i_t) {
            bool do_improve = false;
            do {
              int rand_index = rand() % got->second.size();
              int xp = got->second[rand_index].first;
              int yp = got->second[rand_index].second;
              int mask_pixel = (int) dilated_mask.at<uchar>(yp, xp);
              if (xp >= bew || yp >= beh) {
                do_improve = false;
              } else if (mask_pixel != 255) {
                improve_guess(a, b, ax, ay, xbest, ybest, dbest, xp, yp, 2);
                do_improve = true;
              }
            } while (!do_improve);
          }
        }

        (*ann)[ay][ax] = XY_TO_INT(xbest, ybest);
        (*annd)[ay][ax] = dbest;
      }
    }
  }
}


/**
 * Image inpainting algorithm
 * @param im_orig: original image (with pixels in hole presented or not)
 * @param mask:    mask specify missing region
 * @param constraint: constraint image generate by user
 *
 * @return the completed/inpainting image
 */
void image_complete(Mat im_orig, Mat mask, Mat constraint) {

  // some parameters for scaling
  int rows = im_orig.rows;
  int cols = im_orig.cols;
  //int startscale = (int) -1*ceil(log2(MIN(rows, cols))) + 5;
  int startscale = -3;
  double scale = pow(2, startscale);

  cout << "Scaling image by " << scale << endl;

  double t1 = (double)getTickCount();

  // Resize image to starting scale
  Mat resize_img, resize_mask, resize_constraint;
  resize(im_orig, resize_img, Size(), scale, scale, INTER_AREA);
  resize(mask, resize_mask, Size(), scale, scale, INTER_AREA);
  threshold(resize_mask, resize_mask, 127, 255, 0);
  resize(constraint, resize_constraint, Size(), scale, scale, INTER_NEAREST);


  CMap cm, *cm_ptr;
  cm_ptr = &cm;
  getCMap(resize_constraint, cm_ptr);

  // Random starting guess for inpainted image
  rows = resize_img.rows;
  cols = resize_img.cols;
  for (int y = 0; y < rows; ++y) {
    for (int x = 0; x < cols; ++x) {
      int mask_pixel = (int) resize_mask.at<uchar>(y, x);
      if (mask_pixel != 0 && mask_pixel != 255) {
        cout << "GGGGGGGGGGGGGGG" << endl;
        exit(1);
      }
      // if not black pixel, then means white (1) pixel in mask
      // means hole, thus random init colors in hole
      if (mask_pixel != 0) {
        int const_pixel = (int) resize_constraint.at<uchar>(y, x);
        if (const_pixel == 0) {
          resize_img.at<Vec3b>(y, x)[0] = rand() % 256;
          resize_img.at<Vec3b>(y, x)[1] = rand() % 256;
          resize_img.at<Vec3b>(y, x)[2] = rand() % 256;
        } else {
          unordered_map<int, vector<pair<int, int> > >::iterator got;
          got = cm_ptr->constraint_map.find(const_pixel);
          int rand_index = rand() % got->second.size();
          int nx = got->second[rand_index].first;
          int ny = got->second[rand_index].second;
          Vec3b new_pixel = resize_img.at<Vec3b>(ny, nx);
          resize_img.at<Vec3b>(y, x)[0] = new_pixel[0];
          resize_img.at<Vec3b>(y, x)[1] = new_pixel[1];
          resize_img.at<Vec3b>(y, x)[2] = new_pixel[2];
        }
      }
    }
  }

  double p1 = ((double)getTickCount() - t1) / getTickFrequency();
  cout << "time for init = " << p1 << endl;

  // just for DEBUG
  int index = 0;

  // go through all scale
  for (int logscale = startscale; logscale <= 0; logscale++) {
    index++;

    scale = pow(2, logscale);

    cout << "Scaling is " << scale << endl;

    Box mask_box = getBox(resize_mask);
    // dilate the mask

    Mat element = Mat::zeros(2*patch_w - 1, 2*patch_w - 1, CV_8UC1);
    element(Rect(patch_w - 1, patch_w - 1, patch_w, patch_w)) = 255;
    Mat dilated_mask;
    dilate(resize_mask, dilated_mask, element);

    CMap cmap;
    CMap* cmap_ptr = &cmap;
    getCMap(resize_constraint, cmap_ptr);

    // iterations of image completion
    int im_iterations = 60;
    for (int im_iter = 0; im_iter < im_iterations; ++im_iter) {
      printf("im_iter = %d\n", im_iter);

      BITMAP *ann = NULL, *annd = NULL;

      double t2 = (double)getTickCount();

      Mat B = resize_img.clone();
      bitwise_and(resize_img, 0, B, resize_mask);

      // use patchmatch to find NN
      patchmatch(resize_img, B, ann, annd, dilated_mask, resize_constraint, cmap_ptr);

      double p2 = ((double)getTickCount() - t2) / getTickFrequency();
      cout << "time for PM = " << p2 << endl;

      double t3 =  (double)getTickCount();
      // create new image by letting each patch vote
      Mat R = Mat::zeros(resize_img.rows, resize_img.cols, CV_32FC3);
      Mat Rcount = Mat::zeros(resize_img.rows, resize_img.cols, CV_32FC3);
      for (int y = mask_box.ymin; y < mask_box.ymax; ++y) {
        for (int x = mask_box.xmin; x < mask_box.xmax; ++x) {
            int v = (*ann)[y][x];
            int xbest  = INT_TO_X(v), ybest = INT_TO_Y(v);
            Rect srcRect(Point(x, y), Size(patch_w, patch_w));
            Rect dstRect(Point(xbest, ybest), Size(patch_w, patch_w));
            float d = (float) (*annd)[y][x];
            float sim = exp(-d / (2*pow(sigma, 2) ));
            Mat toAssign;
            addWeighted(R(srcRect), 1.0, resize_img(dstRect), sim, 0, toAssign, CV_32FC3);
            toAssign.copyTo(R(srcRect));
            add(Rcount(srcRect), sim, toAssign, noArray(), CV_32FC3);
            toAssign.copyTo(Rcount(srcRect));

        }
      }
      double p3 = ((double)getTickCount() - t3) / getTickFrequency();
      cout << "time for voting = " << p3 << endl;

      // normalize new image
      // COULD BE optimize TODO
      for (int h = 0; h < R.rows; h++) {
        for (int w = 0; w < R.cols; w++) {
          Vec3f rcount_pixel = Rcount.at<Vec3f>(h, w);
          if (rcount_pixel[0] > 0) {
            Vec3f& r_pixel = R.at<Vec3f>(h, w);
            r_pixel[0] = (r_pixel[0] / rcount_pixel[0]);
            r_pixel[1] = (r_pixel[1] / rcount_pixel[1]);
            r_pixel[2] = (r_pixel[2] / rcount_pixel[2]);
          }
        }
      }

      R.convertTo(R, CV_8UC3);

      // keep pixel outside mask
      Mat old_img = resize_img.clone();
      R.copyTo(resize_img, resize_mask);

      // measure how much image has changed, if not much then stop  TODO
      if (im_iter > 0) {
        double diff = 0;
        int mask_count_white = 0;
        int mask_count_black = 0;
        int mask_count_other = 0;
        for (int h = 0; h < resize_img.rows; h++) {
          for (int w = 0; w < resize_img.cols; w++) {
            int mask_pixel = (int) resize_mask.at<uchar>(h, w);
            // white pixel in mask is hole
            if (mask_pixel == 255) {
              Vec3b new_pixel = resize_img.at<Vec3b>(h, w);
              Vec3b old_pixel = old_img.at<Vec3b>(h, w);
              diff += pow(new_pixel[0] - old_pixel[0], 2);
              diff += pow(new_pixel[1] - old_pixel[1], 2);
              diff += pow(new_pixel[2] - old_pixel[2], 2);
              mask_count_white += 1;
            } else if (mask_pixel == 0) {
              mask_count_black += 1;
            } else {
              mask_count_other += 1;
            }
          }
        }
        assert(mask_count_other == 0);
#ifdef DEBUG
        cout << "diff is " << diff << endl;
        cout << "mask count is " << mask_count_white << endl;
        cout << "norm diff is " << diff/mask_count_white << endl;
#endif
        if (diff/mask_count_white < 0.02) {
          break;
        }
      }

      delete ann;
      delete annd;
    }


    // Upsample A for the next scale
    if (logscale < 0) {
      double t4 = (double)getTickCount();
      cout << "Upscaling" << endl;
      // orig down scale to new scale
      Mat upscale_img;
      resize(im_orig, upscale_img, Size(), 2*scale, 2*scale, INTER_AREA);

      // data upscale to new scale
      int new_cols = upscale_img.cols, new_rows = upscale_img.rows;
      resize(resize_img, resize_img, Size(new_cols, new_rows), 0, 0, INTER_CUBIC);
      resize(mask, resize_mask, Size(new_cols, new_rows), 0, 0, INTER_AREA);
      resize(constraint, resize_constraint, Size(new_cols, new_rows), 0, 0, INTER_NEAREST);

      threshold(resize_mask, resize_mask, 127, 255, 0);

      Mat inverted_mask;
      bitwise_not(resize_mask, inverted_mask);
      upscale_img.copyTo(resize_img, inverted_mask);

      double p4 = ((double)getTickCount() - t4) / getTickFrequency();
      cout << "time for resize = " << p4 << endl;
    }
  }

  imwrite("final_out.png", resize_img);
}

int main(int argc, char *argv[]) {
  argc--;
  argv++;
  if (argc != 3 && argc != 4) { fprintf(stderr, "im_complete a mask result\n"
                                   "Given input image a and mask outputs result\n"
                                   "These are stored as RGB 24-bit images, with a 24-bit int at every pixel."); exit(1); }

  Mat image = imread(argv[0]);

  Mat a_matrix = image.clone();
  Mat mask_cv = imread(argv[1], IMREAD_GRAYSCALE);
  Mat const_cv = imread(argv[2], IMREAD_GRAYSCALE);

  printf("mask_cv type %d\n", mask_cv.type());
  for (int y = 0; y < mask_cv.rows; ++y) {
    for (int x = 0; x < mask_cv.cols; ++x) {
      int mask_pixel =(int) mask_cv.at<uchar>(y, x);
      if (mask_pixel != 0) {
        a_matrix.at<Vec3b>(y, x) = Vec3b(0, 0, 0);
      }
    }
  }

  image_complete(image, mask_cv, const_cv);

  return 0;
}
