# Generated by h2py from /usr/include/sys/socket.h
SOCK_STREAM = 1
SOCK_DGRAM = 2
SOCK_RAW = 3
SOCK_RDM = 4
SOCK_SEQPACKET = 5
SO_DEBUG = 0x0001
SO_ACCEPTCONN = 0x0002
SO_REUSEADDR = 0x0004
SO_KEEPALIVE = 0x0008
SO_DONTROUTE = 0x0010
SO_BROADCAST = 0x0020
SO_USELOOPBACK = 0x0040
SO_LINGER = 0x0080
SO_OOBINLINE = 0x0100
SO_CKSUMRECV = 0x0800
SO_SNDBUF = 0x1001
SO_RCVBUF = 0x1002
SO_SNDLOWAT = 0x1003
SO_RCVLOWAT = 0x1004
SO_SNDTIMEO = 0x1005
SO_RCVTIMEO = 0x1006
SO_ERROR = 0x1007
SO_TYPE = 0x1008
SOL_SOCKET = 0xffff
AF_UNSPEC = 0
AF_UNIX = 1
AF_INET = 2
AF_IMPLINK = 3
AF_PUP = 4
AF_CHAOS = 5
AF_NS = 6
AF_ISO = 7
AF_OSI = AF_ISO
AF_ECMA = 8
AF_DATAKIT = 9
AF_CCITT = 10
AF_SNA = 11
AF_DECnet = 12
AF_DLI = 13
AF_LAT = 14
AF_HYLINK = 15
AF_APPLETALK = 16
AF_ROUTE = 17
AF_LINK = 18
pseudo_AF_XTP = 19
AF_INTF = 20
AF_RIF = 21
AF_NETWARE = 22
AF_NDD = 23
AF_MAX = 30
AF_MAX = 20
PF_UNSPEC = AF_UNSPEC
PF_UNIX = AF_UNIX
PF_INET = AF_INET
PF_IMPLINK = AF_IMPLINK
PF_PUP = AF_PUP
PF_CHAOS = AF_CHAOS
PF_NS = AF_NS
PF_ISO = AF_ISO
PF_OSI = AF_ISO
PF_ECMA = AF_ECMA
PF_DATAKIT = AF_DATAKIT
PF_CCITT = AF_CCITT
PF_SNA = AF_SNA
PF_DECnet = AF_DECnet
PF_DLI = AF_DLI
PF_LAT = AF_LAT
PF_HYLINK = AF_HYLINK
PF_APPLETALK = AF_APPLETALK
PF_ROUTE = AF_ROUTE
PF_LINK = AF_LINK
PF_XTP = pseudo_AF_XTP
PF_INTF = AF_INTF
PF_RIF = AF_RIF
PF_INTF = AF_INTF
PF_NDD = AF_NDD
PF_MAX = AF_MAX
SOMAXCONN = 10
SOMAXCONN = 5
MSG_MAXIOVLEN = 16
UIO_MAXIOV = 1024
UIO_SMALLIOV = 8
MSG_OOB = 0x1
MSG_PEEK = 0x2
MSG_DONTROUTE = 0x4
MSG_EOR = 0x8
MSG_TRUNC = 0x10
MSG_CTRUNC = 0x20
MSG_WAITALL = 0x40
MSG_NONBLOCK = 0x4000
MSG_COMPAT = 0x8000
SCM_RIGHTS = 0x01
