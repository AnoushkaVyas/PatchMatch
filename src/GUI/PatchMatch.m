function varargout = PatchMatch(varargin)
% Patchmatch MATLAB code for GUI for Hole filling application
%      PatchMatch('Callback',hObject,eventdata,handles,...) calls the local
%      function named Callback in PatchMatch.m with the given input arguments.
% hObject    handle to figure1 
% handles    structure with handles and user data 

gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @PatchMatch_OpeningFcn, ...
                   'gui_OutputFcn',  @PatchMatch_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end

% Executes just before PatchMatch is made visible.
function PatchMatch_OpeningFcn(hObject, eventdata, handles, varargin)
% varargin   command line arguments to PatchMatch 

global img;
global msk;
global maskimage;
global draw;
global mskcol;
global wbmFlg;
global point0;
global drawFlg;
global pnSize;
global imSize;
global viewMode;

img = [];
msk = [];
maskimage = [];
mskcol = [0 0 0];
wbmFlg = 0;
point0 = [];
drawFlg = -1;
imSize = [];
pnSize = 5;
viewMode = 1;
% Choose default command line output for PatchMatch
handles.output = hObject;

% Update handles structure
guidata(hObject, handles);

% Outputs from this function are returned to the command line.
function varargout = PatchMatch_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args 
% Get default command line output from handles structure
varargout{1} = handles.output;


function uipanel1_ButtonDownFcn(hObject, eventdata, handles)

% Executes on button press in pushbutton1.
function pushbutton1_Callback(hObject, eventdata, handles)


global filename;
global dir;
[filename, dir] = uigetfile( '*.*', 'Load Image');

if isequal(filename,0)
    return;
end 

global img;
global msk;
global maskimage;
global mskcol;
global wbmFlg;
global point0;
global drawFlg;
global imSize;
global viewMode;

mskcol = [0 0 0];
wbmFlg = 0;
point0 = [];
drawFlg = -1;
viewMode = 1;

img = imread([dir filename]);
imSize = size(img);
msk = zeros(imSize(1),imSize(2),4,'uint8');

maskimage = repmat(img,[1 1 1 4]);

axes(handles.uipanel1);
imshow(img);




function edit1_Callback(hObject, eventdata, handles)

% Executes during object creation, after setting all properties.
function edit1_CreateFcn(hObject, eventdata, handles)
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% Executes during object creation, after setting all properties.
function pushbutton1_CreateFcn(hObject, eventdata, handles)


% Executes on mouse press over figure background, over a disabled or inactive control, or over an axes background.
function figure1_WindowButtonDownFcn(hObject, eventdata, handles)
global drawFlg;
global point0;

mouse = get(gcf,'SelectionType');
if( strcmpi( mouse, 'normal' ) )
    drawFlg = 1;
    point0 = getPixelPosition();

elseif( strcmpi( mouse, 'alt' ) )
    drawFlg = 0;
    point0 = getPixelPosition();

else
    drawFlg = -1;
end


% Executes on mouse motion over figure - except title and menu.
function figure1_WindowButtonMotionFcn(hObject, eventdata, handles)
global pnSize;
global imSize;
global msk;
global point0;
global drawFlg;
global draw;

global wbmFlg;

if( wbmFlg == 0 && drawFlg >= 0 && draw == 1)    
    wbmFlg = 1;
    
    point1 = getPixelPosition();
    
    if( ~isempty( point0 ) )
        ps = pnSize / 480 * max([imSize(1),imSize(2)]);
        msk(:,:,draw) = drawLine( msk(:,:,draw), point0, point1, ps, drawFlg);
        showImageMask(handles.uipanel1); 
    end
    
    point0 = point1;
    
    wbmFlg = 0;
end

% --- Executes on mouse press over figure background, over a disabled or
% --- inactive control, or over an axes background.
function figure1_WindowButtonUpFcn(hObject, eventdata, handles)
% hObject    handle to figure1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
global drawFlg;
global pnSize;
global imSize;
global msk;
global point0;
global draw;

if(draw == 1)
    drawFlg = -1;
    point0 = [];
elseif(~isempty(point0) && ~isempty(imSize))
    ps = pnSize / 480 * max([imSize(1),imSize(2)]);
    point1 = getPixelPosition();
    if(point1(1) <= imSize(1)&&point1(1) > 0&&point1(2) <= imSize(2)&&point1(2) > 0 && point0(1) <= imSize(1)&&point0(1) > 0&&point0(2) <= imSize(2)&&point0(2) > 0)
        msk(:,:,draw) = drawLine( msk(:,:,draw), point0, point1, ps, drawFlg );
        showImageMask(handles.uipanel1);
        point0 = [];
    else
        point0 = [];
        drawFlg = -1;
    end
    
end

function point = getPixelPosition()
global imSize;

if( isempty( imSize ) )
    point = [];
else
    cp = get (gca, 'CurrentPoint');
    cp = cp(1,1:2);
    row = int32(round( axes2pix(imSize(1), [1 imSize(1)], cp(2)) ));
    col = int32(round( axes2pix(imSize(2), [1 imSize(2)], cp(1)) ));

    point = [row col];
end


% --- Executes on button press in pushbutton2.
function pushbutton2_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
global filename;
global dir;
global img;
global msk;
global mskcol;
global draw;

[d name ext] = fileparts(filename);

msk(:,:,1) = uint8(msk(:,:,1)*255);
mskimage = double(img).*double(repmat(~msk(:,:,1),1,1,3));
const = msk(:,:,2)*1+msk(:,:,3)*2+msk(:,:,4)*3;  
imwrite( uint8(mskimage), [name '_img.png'] );
imwrite( uint8(msk(:,:,1)), [name '_msk.png'] );
imwrite( uint8(const), [name '_const.png'] );

cmd = strcat({'./ImageComplete'}, {' '},{name},{'_img.png'},{' '},{name},{'_msk.png'},{' '},{name}, {'_const.png'});
%[status , cmdout] = system(cmd{1});
tic;
system(cmd{1});
toc;

%axes(handles.uipanel1);
comp_img = imread('final_out.png');

global maskimage;
global wbmFlg;
global point0;
global drawFlg;
global imSize;
global viewMode;

mskcol = [0 0 0];
wbmFlg = 0;
point0 = [];
drawFlg = -1;
viewMode = 1;

img = comp_img;
imSize = size(img);
msk = zeros(imSize(1),imSize(2),4,'uint8');
maskimage = repmat(img,[1 1 1 4]);

imshow(comp_img);

function [] = showImageMask(handle)
global img;
global msk;
global mskcol;
global viewMode;
global draw;
global maskimage;


if( ~isempty(img) )
    switch( viewMode )
        case 1
            maskimage(:,:,:,draw) = genImageMask( single(img), single(msk(:,:,draw)), single(mskcol) );
        otherwise
            maskimage(:,:,:,draw) = zeros(size(msk(:,:,draw)));
    end
    
    imshow(uint8(maskimage(:,:,:,draw)));
end


% --- Executes on selection change in popupmenu1.

function popupmenu1_Callback(hObject, eventdata, handles)
% hObject    handle to popupmenu1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns popupmenu1 contents as cell array
%        contents{get(hObject,'Value')} returns selected item from popupmenu1
global draw;
global mskcol;
global maskimage;
global img;

if(~isempty(img))
    draw = get(hObject,'Value');

    switch( draw )
        case 1
            mskcol = [0 0 0];
        case 2
            mskcol = [255 0 0];
        case 3
            mskcol = [0 255 0];
        otherwise
            mskcol = [0 0 255];
    end

    imshow(uint8(maskimage(:,:,:,draw)));
end




% --- Executes during object creation, after setting all properties.
function popupmenu1_CreateFcn(hObject, eventdata, handles)
% hObject    handle to popupmenu1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
global draw;

if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

draw = get(hObject,'Value');


% --- Executes on slider movement.
function slider2_Callback(hObject, eventdata, handles)
% hObject    handle to slider2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'Value') returns position of slider
%        get(hObject,'Min') and get(hObject,'Max') to determine range of slider
global pnSize;
pnSize = 5 + get(hObject,'Value');
set(handles.text2,'String', pnSize);


% --- Executes during object creation, after setting all properties.
function slider2_CreateFcn(hObject, eventdata, handles)
% hObject    handle to slider2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: slider controls usually have a light gray background.
if isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor',[.9 .9 .9]);
end


% --- Executes during object creation, after setting all properties.
function text2_CreateFcn(hObject, eventdata, handles)
% hObject    handle to text2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called


% --- Executes on button press in pushbutton3.
function pushbutton3_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton3 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

global msk;
global maskimage;
global img;
global mskcol;
msk = [];
[filename, dir] = uigetfile( '*.*', 'Load Image');

if isequal(filename,0)
    return;
end 

tmsk = imread([dir filename]);
[x y z] = size(tmsk);
msk = zeros(x,y,4,'uint8');
msk(:,:,1) = tmsk(:,:,1);

maskimage(:,:,:,1) = genImageMask( single(img), single(msk(:,:,1)), single(mskcol) );

axes(handles.uipanel1);
imshow(uint8(maskimage(:,:,:,1)));

