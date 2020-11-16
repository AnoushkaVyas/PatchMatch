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
