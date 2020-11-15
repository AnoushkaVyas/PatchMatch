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