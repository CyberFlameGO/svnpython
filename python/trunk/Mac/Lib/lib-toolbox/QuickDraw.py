# Generated from 'Macintosh HD:SWDev:Metrowerks Codewarrior 6.0:Metrowerks CodeWarrior:MacOS Support:Universal:Interfaces:CIncludes:QuickDraw.h'


def FOUR_CHAR_CODE(x): return x
normal						= 0
bold						= 1
italic						= 2
underline					= 4
outline						= 8
shadow						= 0x10
condense					= 0x20
extend						= 0x40
invalColReq = -1                            
srcCopy = 0
srcOr = 1
srcXor = 2
srcBic = 3
notSrcCopy = 4
notSrcOr = 5
notSrcXor = 6
notSrcBic = 7
patCopy = 8
patOr = 9
patXor = 10
patBic = 11
notPatCopy = 12
notPatOr = 13
notPatXor = 14
notPatBic = 15
grayishTextOr = 49
hilitetransfermode = 50
hilite = 50
blend = 32
addPin = 33
addOver = 34
subPin = 35
addMax = 37
adMax = 37
subOver = 38
adMin = 39
ditherCopy = 64
transparent = 36
italicBit = 1
ulineBit = 2
outlineBit = 3
shadowBit = 4
condenseBit = 5
extendBit = 6
normalBit = 0
inverseBit = 1
redBit = 4
greenBit = 3
blueBit = 2
cyanBit = 8
magentaBit = 7
yellowBit = 6
blackBit = 5
blackColor = 33
whiteColor = 30
redColor = 205
greenColor = 341
blueColor = 409
cyanColor = 273
magentaColor = 137
yellowColor = 69
picLParen = 0
picRParen = 1
clutType = 0
fixedType = 1
directType = 2
gdDevType = 0                             
interlacedDevice = 2
roundedDevice = 5
hasAuxMenuBar = 6
burstDevice = 7
ext32Device = 8
ramInit = 10
mainScreen = 11
allInit = 12
screenDevice = 13
noDriver = 14
screenActive = 15
hiliteBit = 7
pHiliteBit = 0
defQDColors = 127
RGBDirect = 16
baseAddr32 = 4                             
sysPatListID = 0
iBeamCursor = 1
crossCursor = 2
plusCursor = 3
watchCursor = 4
kQDGrafVerbFrame = 0
kQDGrafVerbPaint = 1
kQDGrafVerbErase = 2
kQDGrafVerbInvert = 3
kQDGrafVerbFill = 4
frame = kQDGrafVerbFrame
paint = kQDGrafVerbPaint
erase = kQDGrafVerbErase
invert = kQDGrafVerbInvert
fill = kQDGrafVerbFill
chunky = 0
chunkyPlanar = 1
planar = 2
singleDevicesBit = 0
dontMatchSeedsBit = 1
allDevicesBit = 2
singleDevices = 1 << singleDevicesBit
dontMatchSeeds = 1 << dontMatchSeedsBit
allDevices = 1 << allDevicesBit
kPrinterFontStatus = 0
kPrinterScalingStatus = 1
kNoConstraint = 0
kVerticalConstraint = 1
kHorizontalConstraint = 2
k1MonochromePixelFormat = 0x00000001
k2IndexedPixelFormat = 0x00000002
k4IndexedPixelFormat = 0x00000004
k8IndexedPixelFormat = 0x00000008
k16BE555PixelFormat = 0x00000010
k24RGBPixelFormat = 0x00000018
k32ARGBPixelFormat = 0x00000020
k1IndexedGrayPixelFormat = 0x00000021
k2IndexedGrayPixelFormat = 0x00000022
k4IndexedGrayPixelFormat = 0x00000024
k8IndexedGrayPixelFormat = 0x00000028                    
k16LE555PixelFormat = FOUR_CHAR_CODE('L555')
k16LE5551PixelFormat = FOUR_CHAR_CODE('5551')
k16BE565PixelFormat = FOUR_CHAR_CODE('B565')
k16LE565PixelFormat = FOUR_CHAR_CODE('L565')
k24BGRPixelFormat = FOUR_CHAR_CODE('24BG')
k32BGRAPixelFormat = FOUR_CHAR_CODE('BGRA')
k32ABGRPixelFormat = FOUR_CHAR_CODE('ABGR')
k32RGBAPixelFormat = FOUR_CHAR_CODE('RGBA')
kYUVSPixelFormat = FOUR_CHAR_CODE('yuvs')
kYUVUPixelFormat = FOUR_CHAR_CODE('yuvu')
kYVU9PixelFormat = FOUR_CHAR_CODE('YVU9')
kYUV411PixelFormat = FOUR_CHAR_CODE('Y411')
kYVYU422PixelFormat = FOUR_CHAR_CODE('YVYU')
kUYVY422PixelFormat = FOUR_CHAR_CODE('UYVY')
kYUV211PixelFormat = FOUR_CHAR_CODE('Y211')        
kCursorImageMajorVersion = 0x0001
kCursorImageMinorVersion = 0x0000
kQDParseRegionFromTop = (1 << 0)
kQDParseRegionFromBottom = (1 << 1)
kQDParseRegionFromLeft = (1 << 2)
kQDParseRegionFromRight = (1 << 3)
kQDParseRegionFromTopLeft = kQDParseRegionFromTop | kQDParseRegionFromLeft
kQDParseRegionFromBottomRight = kQDParseRegionFromBottom | kQDParseRegionFromRight
kQDRegionToRectsMsgInit = 1
kQDRegionToRectsMsgParse = 2
kQDRegionToRectsMsgTerminate = 3
colorXorXFer = 52
noiseXFer = 53
customXFer = 54
kXFer1PixelAtATime = 0x00000001
kXFerConvertPixelToRGB32 = 0x00000002                    
kCursorComponentsVersion = 0x00010001
kCursorComponentType = FOUR_CHAR_CODE('curs')
cursorDoesAnimate = 1L << 0
cursorDoesHardware = 1L << 1
cursorDoesUnreadableScreenBits = 1L << 2
kRenderCursorInHardware = 1L << 0
kRenderCursorInSoftware = 1L << 1
kCursorComponentInit = 0x0001
kCursorComponentGetInfo = 0x0002
kCursorComponentSetOutputMode = 0x0003
kCursorComponentSetData = 0x0004
kCursorComponentReconfigure = 0x0005
kCursorComponentDraw = 0x0006
kCursorComponentErase = 0x0007
kCursorComponentMove = 0x0008
kCursorComponentAnimate = 0x0009
kCursorComponentLastReserved = 0x0050
# Generated from 'Macintosh HD:SWDev:Metrowerks Codewarrior 6.0:Metrowerks CodeWarrior:MacOS Support:Universal:Interfaces:CIncludes:QuickDrawText.h'


def FOUR_CHAR_CODE(x): return x
normal						= 0
bold						= 1
italic						= 2
underline					= 4
outline						= 8
shadow						= 0x10
condense					= 0x20
extend						= 0x40
leftCaret = 0
rightCaret = -1
kHilite = 1                             
smLeftCaret = 0
smRightCaret = -1
smHilite = 1                             
onlyStyleRun = 0
leftStyleRun = 1
rightStyleRun = 2
middleStyleRun = 3
smOnlyStyleRun = 0
smLeftStyleRun = 1
smRightStyleRun = 2
smMiddleStyleRun = 3                             
tfAntiAlias = 1 << 0
tfUnicode = 1 << 1
