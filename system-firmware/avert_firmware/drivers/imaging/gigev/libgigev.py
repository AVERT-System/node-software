#
# ====================================================
#
# pygigev.py
#
# Wrap the GigE-V Framework library using "ctypes"
#

import enum
import ctypes

gevlib_libname = "libGevApi.so"
gevlib_lib = ctypes.CDLL(gevlib_libname)



# ========================================================================================================
#
# enum definitions....
#

# typedef enum
# {
# GevMonitorMode = 0,
# GevControlMode = 2,
# GevExclusiveMode = 4
# } GevAccessMode;

# GevAccessNode enum
(GevMonitorMode, GevControlMode, GevExclusiveMode) = (0, 2, 4)

# // Buffer cycling control definition
# typedef enum
# {
# Asynchronous = 0,
# SynchronousNextEmpty = 1
# } GevBufferCyclingMode;
(Asynchronous, SynchronousNextEmpty) = (0, 1)


class GevPixelFormats(enum.Enum):
    fmtMono8 = 0x01080001
    fmtMono8Signed = 0x01080002
    fmtMono10 = 0x01100003
    fmtMono10Packed = 0x010C0004
    fmtMono12 = 0x01100005
    fmtMono12Packed = 0x010C0006
    fmtMono14 = 0x01100025
    fmtMono16 = 0x01100007
    fmtBayerGR8 = 0x01080008
    fmtBayerRG8 = 0x01080009
    fmtBayerGB8 = 0x0108000A
    fmtBayerBG8 = 0x0108000B
    fmtBayerGR10 = 0x0110000C
    fmtBayerRG10 = 0x0110000D
    fmtBayerGB10 = 0x0110000E
    fmtBayerBG10 = 0x0110000F
    fmtBayerGR10Packed = 0x010C0026
    fmtBayerRG10Packed = 0x010C0027
    fmtBayerGB10Packed = 0x010C0028
    fmtBayerBG10Packed = 0x010C0029
    fmtBayerGR12 = 0x01100010
    fmtBayerRG12 = 0x01100011
    fmtBayerGB12 = 0x01100012
    fmtBayerBG12 = 0x01100013
    fmtBayerGR12Packed = 0x010C002A
    fmtBayerRG12Packed = 0x010C002B
    fmtBayerGB12Packed = 0x010C002C
    fmtBayerBG12Packed = 0x010C002D
    fmtRGB8Packed = 0x02180014
    fmtBGR8Packed = 0x02180015
    fmtRGBA8Packed = 0x02200016
    fmtBGRA8Packed = 0x02200017
    fmtRGB10Packed = 0x02300018
    fmtBGR10Packed = 0x02300019
    fmtRGB12Packed = 0x0230001A
    fmtBGR12Packed = 0x0230001B
    fmtRGB14Packed = 0x0230005E
    fmtBGR14Packed = 0x0230004A
    fmtRGB16Packed = 0x02300033
    fmtBGR16Packed = 0x0230004B
    fmtRGBA16Packed = 0x02400064
    fmtBGRA16Packed = 0x02400051
    fmtRGB10V1Packed = 0x0220001C
    fmtRGB10V2Packed = 0x0220001D
    fmtYUV411packed = 0x020C001E
    fmtYUV422packed = 0x0210001F
    fmtYUV444packed = 0x02180020
    fmt_PFNC_YUV422_8 = 0x02100032
    fmtRGB8Planar = 0x02180021
    fmtRGB10Planar = 0x02300022
    fmtRGB12Planar = 0x02300023
    fmtRGB16Planar = 0x02300024
    fmt_PFNC_BiColorBGRG8 = 0x021000A6
    fmt_PFNC_BiColorBGRG10 = 0x022000A9
    fmt_PFNC_BiColorBGRG10p = 0x021400AA
    fmt_PFNC_BiColorBGRG12 = 0x022000AD
    fmt_PFNC_BiColorBGRG12p = 0x021800AE
    fmt_PFNC_BiColorRGBG8 = 0x021000A5
    fmt_PFNC_BiColorRGBG10 = 0x022000A7
    fmt_PFNC_BiColorRGBG10p = 0x021400A8
    fmt_PFNC_BiColorRGBG12 = 0x022000AB
    fmt_PFNC_BiColorRGBG12p = 0x021800AC


# ========================================================================================================
#
# Structure definitions....
#
# typedef struct
# {
# UINT32 version;
# UINT32 logLevel;
# UINT32 numRetries;
# UINT32 command_timeout_ms;
# UINT32 discovery_timeout_ms;
# UINT32 enumeration_port;
# UINT32 gvcp_port_range_start;
# UINT32 gvcp_port_range_end;
# UINT32 manual_xml_handling;
# } GEVLIB_CONFIG_OPTIONS, *PGEVLIB_CONFIG_OPTIONS;


class GEVLIB_CONFIG_OPTIONS(ctypes.Structure):
    _fields_ = [
        ("version", ctypes.c_uint32),
        ("logLevel", ctypes.c_uint32),
        ("numRetries", ctypes.c_uint32),
        ("command_timeout_ms", ctypes.c_uint32),
        ("discovery_timeout_ms", ctypes.c_uint32),
        ("enumeration_port", ctypes.c_uint32),
        ("gvcp_port_range_start", ctypes.c_uint32),
        ("gvcp_port_range_end", ctypes.c_uint32),
        ("manual_xml_handling", ctypes.c_uint32),
    ]


# typedef struct
# {
# UINT32 numRetries;
# UINT32 command_timeout_ms;
# UINT32 heartbeat_timeout_ms;
# UINT32 streamPktSize;				// GVSP max packet size ( less than or equal to MTU size).
# UINT32 streamPktDelay;				// Delay between packets (microseconds) - to tune packet pacing out of NIC.
# UINT32 streamNumFramesBuffered;	// # of frames to buffer (min 2)
# UINT32 streamMemoryLimitMax;		// Maximum amount of memory to use (puts an upper limit on the # of frames to buffer).
# UINT32 streamMaxPacketResends;	// Maximum number of packet resends to allow for a frame (defaults to 1000).
# UINT32 streamFrame_timeout_ms;	// Frame timeout (msec) after leader received.
# INT32  streamThreadAffinity;		// CPU affinity for streaming thread (marshall/unpack/write to user buffer) - default handling is "-1"
# INT32  serverThreadAffinity;		// CPU affinity for packet server thread (recv/dispatch) - default handling is "-1"
# UINT32 msgChannel_timeout_ms;
# UINT32 enable_passthru_mode;		// Zero (default) to enable automatic conversion of packed pixel formats to unpacked pixel format.
# // Non-zero for passthru mode.
# // (Use Unpacked pixels for processing, Use Packed pixels for archiving to save space)
# } GEV_CAMERA_OPTIONS, *PGEV_CAMERA_OPTIONS;


class GEV_CAMERA_OPTIONS(ctypes.Structure):
    _fields_ = [
        ("numRetries", ctypes.c_uint32),
        ("command_timeout_ms", ctypes.c_uint32),
        ("heartbeat_timeout_ms", ctypes.c_uint32),
        ("streamPktSize", ctypes.c_uint32),
        ("streamPktDelay", ctypes.c_uint32),
        ("streamNumFramesBuffered", ctypes.c_uint32),
        ("streamMemoryLimitMax", ctypes.c_uint32),
        ("streamMaxPacketResends", ctypes.c_uint32),
        ("streamFrame_timeout_ms", ctypes.c_uint32),
        ("streamThreadAffinity", ctypes.c_int32),
        ("serverThreadAffinity", ctypes.c_int32),
        ("msgChannel_timeout_ms", ctypes.c_uint32),
        ("enable_passthru_mode", ctypes.c_uint32),
    ]


# typedef struct
# {
# BOOL fIPv6;				// GEV is only IPv4 for now.
# UINT32 ipAddr;
# UINT32 ipAddrLow;
# UINT32 ipAddrHigh;
# UINT32 ifIndex;		// Index of network interface (set by system - required for packet interface access).
# } GEV_NETWORK_INTERFACE, *PGEV_NETWORK_INTERFACE;
#
# #define MAX_GEVSTRING_LENGTH	64

(MAX_GEVSTRING_LENGTH) = 65


class GEV_NETWORK_INTERFACE(ctypes.Structure):
    _fields_ = [
        ("fIPv6", ctypes.c_uint32),
        ("ipAddr", ctypes.c_uint32),
        ("ipAddrLow", ctypes.c_uint32),
        ("ipAddrHig", ctypes.c_uint32),
        ("fIPv6", ctypes.c_uint32),
    ]


# typedef struct
# {
# BOOL fIPv6;				// GEV is only IPv4 for now.
# UINT32 ipAddr;
# UINT32 ipAddrLow;
# UINT32 ipAddrHigh;
# UINT32 macLow;
# UINT32 macHigh;
# GEV_NETWORK_INTERFACE host;
# UINT32 mode;
# UINT32 capabilities;
# char   manufacturer[MAX_GEVSTRING_LENGTH+1];
# char   model[MAX_GEVSTRING_LENGTH+1];
# char   serial[MAX_GEVSTRING_LENGTH+1];
# char   version[MAX_GEVSTRING_LENGTH+1];
# char   username[MAX_GEVSTRING_LENGTH+1];
# } GEV_DEVICE_INTERFACE, *PGEV_DEVICE_INTERFACE, GEV_CAMERA_INFO, *PGEV_CAMERA_INFO;


class GEV_CAMERA_INFO(ctypes.Structure):
    _fields_ = [
        ("fIPv6", ctypes.c_uint32),
        ("ipAddr", ctypes.c_uint32),
        ("ipAddrLow", ctypes.c_int32),
        ("ipAddrHigh", ctypes.c_uint32),
        ("macLow", ctypes.c_uint32),
        ("macHigh", ctypes.c_uint32),
        ("host", GEV_NETWORK_INTERFACE),
        ("mode", ctypes.c_uint32),
        ("capabilities", ctypes.c_uint32),
        ("w", ctypes.c_int32),
        ("manufacturer", ctypes.c_char * 65),
        ("model", ctypes.c_char * 65),
        ("serial", ctypes.c_char * 65),
        ("version", ctypes.c_char * 65),
        ("username", ctypes.c_char * 65),
    ]


# // Buffer object structure - returned
# typedef struct _tag_GEVBUF_ENTRY
# {
# UINT32 payload_type;	// Type of payload received (???list them ???)
# UINT32 state;			// Full/empty state for payload buffer (tag used for buffer cycling)
# INT32  status;			// Frame Status (success, error types)
# UINT32 timestamp_hi;	// Most 32 significant bit of the timestamp (for legacy code) .
# UINT32 timestamp_lo;	// Least 32 significant bit of the timestamp (for legacy code) .
# UINT64 timestamp; 	// 64bit version of timestamp for payload (device level timestamp using device level timebase).
# UINT64 recv_size;		// Received size of entire payload (including all appended "chunk" (metadata) information) .
# UINT64 id;				// Block id for the payload (starts at 1, may wrap to 1 at 65535 - depending on the payload type).
# // Image specific payload entries.
# UINT32 h;				// Received height (lines) for an image payload.
# UINT32 w;				// Received width (pixels) for an image payload.
# UINT32 x_offset;		// Received x offset for origin of ROI for an image payload_type.
# UINT32 y_offset;		// Received y offset for origin of ROI for an image payload_type.
# UINT32 x_padding;		// Received x padding bytes for an image payload_type (invalid data padding end of each line [horizontal invalid]).
# UINT32 y_padding;		// Received y padding bytes for an image payload_type (invalid data padding end of image [vertical invalid]).
# UINT32 d;				// Received pixel depth (bytes per pixel) for an image payload with a Gige Vision defined pixel format.
# UINT32 format;			// Received Gige Vision pixel format for image or JPEG data types.
# // (If the format value is not a valid Gige Vision pixel type and the payload_type is JPEG, then the format value
# //  is to be interpreted as a color space value (EnumCS value for JPEG) to be used by a JPEG decoder).
# //
# PUINT8 address;		// Address of the "payload_type" data, NULL if the payload has been sent to trash (no buffer available to receive it).
# //
# // New entries for non-image payload types
# //
# PUINT8 chunk_data;	// Address of "chunk" data (metadata) associated with the received payload (NULL if no "chunk" data (metadata) is available).
# // (The "chunk_data" address is provided here as a shortcut. It is the address immediatley following the end of "paylod_type" data)
# UINT32 chunk_size;	// The size of the chunk_data (uncompressed). Zero if no "chunk" data (metadata) is available.
# // (The "chunk_size" is provided as a helper for decoding raw TurboDrive compressed data in passthru mode).
# //
# char  filename[256];	// Name of file for payload type "file" (0 terminated string, 255 characters maximum system limit in Linux).
# } GEVBUF_ENTRY, *PGEVBUF_ENTRY, GEVBUF_HEADER, *PGEVBUF_HEADER, GEV_BUFFER_OBJECT, *PGEV_BUFFER_OBJECT;


class GEV_BUFFER_OBJECT(ctypes.Structure):
    _fields_ = [
        ("payload_type", ctypes.c_uint32),
        ("state", ctypes.c_uint32),
        ("status", ctypes.c_int32),
        ("timestamp_hi", ctypes.c_uint32),
        ("timestamp_lo", ctypes.c_uint32),
        ("timestamp", ctypes.c_uint64),
        ("recv_size", ctypes.c_uint64),
        ("id", ctypes.c_uint64),
        ("h", ctypes.c_uint32),
        ("w", ctypes.c_int32),
        ("x_offset", ctypes.c_uint32),
        ("y_offset", ctypes.c_int32),
        ("x_padding", ctypes.c_uint32),
        ("y_padding", ctypes.c_int32),
        ("d", ctypes.c_uint32),
        ("format", ctypes.c_int32),
        ("address", ctypes.c_void_p),
        ("chunk_data", ctypes.c_void_p),
        ("chunk_size", ctypes.c_uint32),
        ("filename", ctypes.c_char * 256),
    ]


# ===================================================================================
#
# API functions themselves....
#

# GEV_STATUS	GevApiInitialize(void);
#
GevApiInitialize = gevlib_lib.GevApiInitialize
# GevApiInitialize.argtypes = (ctypes.c_void)
GevApiInitialize.restype = ctypes.c_int

# GEV_STATUS	GevApiUninitialize(void);
#
GevApiUninitialize = gevlib_lib.GevApiUninitialize
# GevApiUninitialize.argtypes = (ctypes.c_void)
GevApiUninitialize.restype = ctypes.c_int


# GEV_STATUS GevGetLibraryConfigOptions( GEVLIB_CONFIG_OPTIONS *options);
#
GevGetLibraryConfigOptions = gevlib_lib.GevGetLibraryConfigOptions
GevGetLibraryConfigOptions.argtypes = [ctypes.POINTER(GEVLIB_CONFIG_OPTIONS)]
GevGetLibraryConfigOptions.restype = ctypes.c_int


# GEV_STATUS GevSetLibraryConfigOptions( GEVLIB_CONFIG_OPTIONS *options);
#
GevSetLibraryConfigOptions = gevlib_lib.GevSetLibraryConfigOptions
GevSetLibraryConfigOptions.argtypes = [ctypes.POINTER(GEVLIB_CONFIG_OPTIONS)]
GevSetLibraryConfigOptions.restype = ctypes.c_int


# int GevDeviceCount(void);	// Get the number of Gev devices seen by the system.
#
GevDeviceCount = gevlib_lib.GevDeviceCount
# GevDeviceCount.argtypes = ctypes.c_void
GevDeviceCount.restype = ctypes.c_int


# GEV_STATUS GevGetCameraList( GEV_CAMERA_INFO *cameras, int maxCameras, int *numCameras); // Automatically detect and list cameras.
#
GevGetCameraList = gevlib_lib.GevGetCameraList
GevGetCameraList.argtypes = [
    ctypes.POINTER(GEV_CAMERA_INFO),
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_uint32),
]
GevGetCameraList.restype = ctypes.c_int

# GEV_STATUS GevOpenCamera( GEV_CAMERA_INFO *device, GevAccessMode mode, GEV_CAMERA_HANDLE *handle);
#
GevOpenCamera = gevlib_lib.GevOpenCamera
GevOpenCamera.argtypes = [
    ctypes.POINTER(GEV_CAMERA_INFO),
    ctypes.c_uint32,
    ctypes.c_void_p,
]
GevOpenCamera.restype = ctypes.c_int

# GEV_STATUS GevOpenCameraByAddress( unsigned long ip_address, GevAccessMode mode, GEV_CAMERA_HANDLE *handle);
#
GevOpenCameraByAddress = gevlib_lib.GevOpenCameraByAddress
GevOpenCameraByAddress.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p]
GevOpenCameraByAddress.restype = ctypes.c_int

# GEV_STATUS GevOpenCameraByName( char *name, GevAccessMode mode, GEV_CAMERA_HANDLE *handle);
#
GevOpenCameraByName = gevlib_lib.GevOpenCameraByName
GevOpenCameraByName.argtypes = [ctypes.c_char_p, ctypes.c_uint32, ctypes.c_void_p]
GevOpenCameraByName.restype = ctypes.c_int

# GEV_STATUS GevOpenCameraBySN( char *sn, GevAccessMode mode, GEV_CAMERA_HANDLE *handle);
#
GevOpenCameraBySN = gevlib_lib.GevOpenCameraBySN
GevOpenCameraBySN.argtypes = [ctypes.c_char_p, ctypes.c_uint32, ctypes.c_void_p]
GevOpenCameraBySN.restype = ctypes.c_int

# GEV_STATUS GevCloseCamera(GEV_CAMERA_HANDLE *handle);
#
GevCloseCamera = gevlib_lib.GevCloseCamera
GevCloseCamera.argtypes = [ctypes.c_void_p]
GevCloseCamera.restype = ctypes.c_int


# GEV_STATUS GevGetCameraInterfaceOptions( GEV_CAMERA_HANDLE handle, GEV_CAMERA_OPTIONS *options);
#
GevGetCameraInterfaceOptions = gevlib_lib.GevGetCameraInterfaceOptions
GevGetCameraInterfaceOptions.argtypes = [
    ctypes.c_void_p,
    ctypes.POINTER(GEV_CAMERA_OPTIONS),
]
GevGetCameraInterfaceOptions.restype = ctypes.c_int

# GEV_STATUS GevSetCameraInterfaceOptions( GEV_CAMERA_HANDLE handle, GEV_CAMERA_OPTIONS *options);
#
GevSetCameraInterfaceOptions = gevlib_lib.GevSetCameraInterfaceOptions
GevSetCameraInterfaceOptions.argtypes = [
    ctypes.c_void_p,
    ctypes.POINTER(GEV_CAMERA_OPTIONS),
]
GevSetCameraInterfaceOptions.restype = ctypes.c_int


# GEV_STATUS GevGetFeatureValue( GEV_CAMERA_HANDLE handle, const char *feature_name, int *feature_type, int value_size, void *value);
#
GevGetFeatureValue = gevlib_lib.GevGetFeatureValue
GevGetFeatureValue.argtypes = [
    ctypes.c_void_p,
    ctypes.c_char_p,
    ctypes.POINTER(ctypes.c_int),
    ctypes.c_int,
    ctypes.c_void_p,
]
GevGetFeatureValue.restype = ctypes.c_int

# GEV_STATUS GevSetFeatureValue( GEV_CAMERA_HANDLE handle, const char *feature_name, int value_size, void *value);
#
GevSetFeatureValue = gevlib_lib.GevSetFeatureValue
GevSetFeatureValue.argtypes = [
    ctypes.c_void_p,
    ctypes.c_char_p,
    ctypes.c_int,
    ctypes.c_void_p,
]
GevSetFeatureValue.restype = ctypes.c_int

# GEV_STATUS GevGetFeatureValueAsString( GEV_CAMERA_HANDLE handle, const char *feature_name, int *feature_type, int value_string_size, char *value_string);
#
GevGetFeatureValueAsString = gevlib_lib.GevGetFeatureValueAsString
GevGetFeatureValueAsString.argtypes = [
    ctypes.c_void_p,
    ctypes.c_char_p,
    ctypes.POINTER(ctypes.c_int),
    ctypes.c_int,
    ctypes.c_char_p,
]
GevGetFeatureValueAsString.restype = ctypes.c_int


# GEV_STATUS GevSetFeatureValueAsString( GEV_CAMERA_HANDLE handle, const char *feature_name, const char *value_string);
#
GevSetFeatureValueAsString = gevlib_lib.GevSetFeatureValueAsString
GevSetFeatureValueAsString.argtypes = [
    ctypes.c_void_p,
    ctypes.c_char_p,
    ctypes.c_char_p,
]
GevSetFeatureValueAsString.restype = ctypes.c_int

# ==========================================================
# All the transfer stuff....
#

# GEV_STATUS GevInitializeTransfer( GEV_CAMERA_HANDLE handle, GevBufferCyclingMode mode, UINT64 bufSize, UINT32 numBuffers, UINT8 **bufAddress);
#
GevInitializeTransfer = gevlib_lib.GevInitializeTransfer
GevInitializeTransfer.argtypes = [
    ctypes.c_void_p,
    ctypes.c_uint32,
    ctypes.c_uint64,
    ctypes.c_uint32,
    ctypes.c_void_p,
]
GevInitializeTransfer.restype = ctypes.c_int

# GEV_STATUS GevGetPayloadParameters(GEV_CAMERA_HANDLE handle, PUINT64 payload_size, PUINT32 data_format);
#
GevGetPayloadParameters = gevlib_lib.GevGetPayloadParameters
GevGetPayloadParameters.argtypes = [
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_uint64),
    ctypes.POINTER(ctypes.c_uint32),
]
GevGetPayloadParameters.restype = ctypes.c_int

# GEV_STATUS GevFreeTransfer( GEV_CAMERA_HANDLE handle);
#
GevFreeTransfer = gevlib_lib.GevFreeTransfer
GevFreeTransfer.argtypes = [ctypes.c_void_p]
GevFreeTransfer.restype = ctypes.c_int

# GEV_STATUS GevStartTransfer( GEV_CAMERA_HANDLE handle, UINT32 numFrames);
#
GevStartTransfer = gevlib_lib.GevStartTransfer
GevStartTransfer.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
GevStartTransfer.restype = ctypes.c_int

# GEV_STATUS GevStopTransfer( GEV_CAMERA_HANDLE handle);
#
GevStopTransfer = gevlib_lib.GevStopTransfer
GevStopTransfer.argtypes = [ctypes.c_void_p]
GevStopTransfer.restype = ctypes.c_int

# GEV_STATUS GevAbortTransfer( GEV_CAMERA_HANDLE handle);
#
GevAbortTransfer = gevlib_lib.GevAbortTransfer
GevAbortTransfer.argtypes = [ctypes.c_void_p]
GevAbortTransfer.restype = ctypes.c_int


# GEV_STATUS GevWaitForNextFrame( GEV_CAMERA_HANDLE handle, GEV_BUFFER_OBJECT **frame_object, UINT32 timeout);
#
GevWaitForNextFrame = gevlib_lib.GevWaitForNextFrame
GevWaitForNextFrame.argtypes = [
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.POINTER(GEV_BUFFER_OBJECT)),
    ctypes.c_uint32,
]
GevWaitForNextFrame.restype = ctypes.c_int

# ???heredummy - is this correct way to get pointer to pointer ?????

# GEV_STATUS GevReleaseFrame( GEV_CAMERA_HANDLE handle, GEV_BUFFER_OBJECT *frame_object_ptr);
#
GevReleaseFrame = gevlib_lib.GevReleaseFrame
GevReleaseFrame.argtypes = [ctypes.c_void_p, ctypes.POINTER(GEV_BUFFER_OBJECT)]
GevReleaseFrame.restype = ctypes.c_int

# GEV_STATUS GevReleaseFrameBuffer( GEV_CAMERA_HANDLE handle, void *frame_buffer_ptr);
#
GevReleaseFrameBuffer = gevlib_lib.GevReleaseFrameBuffer
GevReleaseFrameBuffer.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
GevReleaseFrameBuffer.restype = ctypes.c_int

# GEV_STATUS GevQueryTransferStatus( GEV_CAMERA_HANDLE handle, PUINT32 pTotalBuffers, PUINT32 pNumUsed, PUINT32 pNumFree, PUINT32 pNumTrashed, GevBufferCyclingMode *pMode);
#
GevQueryTransferStatus = gevlib_lib.GevQueryTransferStatus
GevQueryTransferStatus.argtypes = [
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.POINTER(ctypes.c_uint32),
]
GevQueryTransferStatus.restype = ctypes.c_int


# ==========================================================
# Pixel format info functions....
#
# BOOL GevIsPixelTypeMono( UINT32 pixelType);
#
GevIsPixelTypeMono = gevlib_lib.GevIsPixelTypeMono
GevIsPixelTypeMono.argtypes = [ctypes.c_uint32]
GevIsPixelTypeMono.restype = ctypes.c_int

# BOOL GevIsPixelTypeRGB( UINT32 pixelType);
#
GevIsPixelTypeRGB = gevlib_lib.GevIsPixelTypeRGB
GevIsPixelTypeRGB.argtypes = [ctypes.c_uint32]
GevIsPixelTypeRGB.restype = ctypes.c_int

# BOOL GevIsPixelTypeBayer (UINT32 pixelType);
#
GevIsPixelTypeBayer = gevlib_lib.GevIsPixelTypeBayer
GevIsPixelTypeBayer.argtypes = [ctypes.c_uint32]
GevIsPixelTypeBayer.restype = ctypes.c_int

# BOOL GevIsPixelTypePacked( UINT32 pixelType);
#
GevIsPixelTypePacked = gevlib_lib.GevIsPixelTypePacked
GevIsPixelTypePacked.argtypes = [ctypes.c_uint32]
GevIsPixelTypePacked.restype = ctypes.c_int

# UINT32 GevGetPixelSizeInBytes( UINT32 pixelType);
#
GevGetPixelSizeInBytes = gevlib_lib.GevGetPixelSizeInBytes
GevGetPixelSizeInBytes.argtypes = [ctypes.c_uint32]
GevGetPixelSizeInBytes.restype = ctypes.c_uint32

# UINT32 GevGetPixelDepthInBits( UINT32 pixelType);
#
GevGetPixelDepthInBits = gevlib_lib.GevGetPixelDepthInBits
GevGetPixelDepthInBits.argtypes = [ctypes.c_uint32]
GevGetPixelDepthInBits.restype = ctypes.c_uint32

# UINT32 GevGetUnpackedPixelType(UINT32 pixelType);
#
GevGetUnpackedPixelType = gevlib_lib.GevGetUnpackedPixelType
GevGetUnpackedPixelType.argtypes = [ctypes.c_uint32]
GevGetUnpackedPixelType.restype = ctypes.c_uint32

# UINT32 GevGetPixelComponentCount(UINT32 pixelType);
#
GevGetPixelComponentCount = gevlib_lib.GevGetPixelComponentCount
GevGetPixelComponentCount.argtypes = [ctypes.c_uint32]
GevGetPixelComponentCount.restype = ctypes.c_uint32

# UINT32 GevGetConvertedPixelType(int convertBayer, UINT32 pixelType);
#
GevGetConvertedPixelType = gevlib_lib.GevGetConvertedPixelType
GevGetConvertedPixelType.argtypes = [ctypes.c_int, ctypes.c_uint32]
GevGetConvertedPixelType.restype = ctypes.c_uint32

# ==========================================================
# Event callbacks ....
#

# GEV_STATUS GevRegisterEventCallback(GEV_CAMERA_HANDLE handle,  UINT32 EventID, GEVEVENT_CBFUNCTION func, void *context);
#
GevRegisterEventCallback = gevlib_lib.GevRegisterEventCallback
GevRegisterEventCallback.argtypes = [
    ctypes.c_void_p,
    ctypes.c_uint32,
    ctypes.c_void_p,
    ctypes.c_void_p,
]
GevRegisterEventCallback.restype = ctypes.c_uint32

# GEV_STATUS GevUnregisterEvent(GEV_CAMERA_HANDLE handle,  UINT32 EventID);
#
GevUnregisterEvent = gevlib_lib.GevUnregisterEvent
GevUnregisterEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
GevUnregisterEvent.restype = ctypes.c_uint32
