# Generated by h2py from /usr/include/netinet/in.h
_NETINET_IN_H = 1

# Included from features.h
_FEATURES_H = 1
_GNU_SOURCE = 1
__USE_ANSI = 1
__FAVOR_BSD = 1
_BSD_SOURCE = 1
_SVID_SOURCE = 1
_POSIX_SOURCE = 1
_POSIX_C_SOURCE = 2
__USE_POSIX = 1
__USE_POSIX2 = 1
__USE_MISC = 1
__USE_BSD = 1
__USE_SVID = 1
__USE_GNU = 1
__GNU_LIBRARY__ = 1

# Included from sys/cdefs.h
_SYS_CDEFS_H = 1
def __P(args): return args	 

def __P(args): return args

def __P(args): return ()	 

def __STRING(x): return #x

def __STRING(x): return "x"


# Included from sys/socket.h

# Included from linux/socket.h

# Included from asm/socket.h

# Included from asm/sockios.h
FIOSETOWN = 0x8901
SIOCSPGRP = 0x8902
FIOGETOWN = 0x8903
SIOCGPGRP = 0x8904
SIOCATMARK = 0x8905
SIOCGSTAMP = 0x8906
SOL_SOCKET = 1
SO_DEBUG = 1
SO_REUSEADDR = 2
SO_TYPE = 3
SO_ERROR = 4
SO_DONTROUTE = 5
SO_BROADCAST = 6
SO_SNDBUF = 7
SO_RCVBUF = 8
SO_KEEPALIVE = 9
SO_OOBINLINE = 10
SO_NO_CHECK = 11
SO_PRIORITY = 12
SO_LINGER = 13
SO_BSDCOMPAT = 14

# Included from linux/sockios.h
SIOCADDRT = 0x890B
SIOCDELRT = 0x890C
SIOCGIFNAME = 0x8910
SIOCSIFLINK = 0x8911
SIOCGIFCONF = 0x8912
SIOCGIFFLAGS = 0x8913
SIOCSIFFLAGS = 0x8914
SIOCGIFADDR = 0x8915
SIOCSIFADDR = 0x8916
SIOCGIFDSTADDR = 0x8917
SIOCSIFDSTADDR = 0x8918
SIOCGIFBRDADDR = 0x8919
SIOCSIFBRDADDR = 0x891a
SIOCGIFNETMASK = 0x891b
SIOCSIFNETMASK = 0x891c
SIOCGIFMETRIC = 0x891d
SIOCSIFMETRIC = 0x891e
SIOCGIFMEM = 0x891f
SIOCSIFMEM = 0x8920
SIOCGIFMTU = 0x8921
SIOCSIFMTU = 0x8922
SIOCSIFHWADDR = 0x8924
SIOCGIFENCAP = 0x8925
SIOCSIFENCAP = 0x8926
SIOCGIFHWADDR = 0x8927
SIOCGIFSLAVE = 0x8929
SIOCSIFSLAVE = 0x8930
SIOCADDMULTI = 0x8931
SIOCDELMULTI = 0x8932
SIOCGIFBR = 0x8940
SIOCSIFBR = 0x8941
OLD_SIOCDARP = 0x8950
OLD_SIOCGARP = 0x8951
OLD_SIOCSARP = 0x8952
SIOCDARP = 0x8953
SIOCGARP = 0x8954
SIOCSARP = 0x8955
SIOCDRARP = 0x8960
SIOCGRARP = 0x8961
SIOCSRARP = 0x8962
SIOCGIFMAP = 0x8970
SIOCSIFMAP = 0x8971
SIOCADDDLCI = 0x8980
SIOCDELDLCI = 0x8981
SIOCDEVPRIVATE = 0x89F0
SIOCPROTOPRIVATE = 0x89E0

# Included from linux/uio.h
UIO_MAXIOV = 16
SCM_RIGHTS = 1
SOCK_STREAM = 1
SOCK_DGRAM = 2
SOCK_RAW = 3
SOCK_RDM = 4
SOCK_SEQPACKET = 5
SOCK_PACKET = 10
AF_UNSPEC = 0
AF_UNIX = 1
AF_INET = 2
AF_AX25 = 3
AF_IPX = 4
AF_APPLETALK = 5
AF_NETROM = 6
AF_BRIDGE = 7
AF_AAL5 = 8
AF_X25 = 9
AF_INET6 = 10
AF_MAX = 12
PF_UNSPEC = AF_UNSPEC
PF_UNIX = AF_UNIX
PF_INET = AF_INET
PF_AX25 = AF_AX25
PF_IPX = AF_IPX
PF_APPLETALK = AF_APPLETALK
PF_NETROM = AF_NETROM
PF_BRIDGE = AF_BRIDGE
PF_AAL5 = AF_AAL5
PF_X25 = AF_X25
PF_INET6 = AF_INET6
PF_MAX = AF_MAX
SOMAXCONN = 128
MSG_OOB = 1
MSG_PEEK = 2
MSG_DONTROUTE = 4
MSG_PROXY = 16
SOL_IP = 0
SOL_IPX = 256
SOL_AX25 = 257
SOL_ATALK = 258
SOL_NETROM = 259
SOL_TCP = 6
SOL_UDP = 17
IP_TOS = 1
IPTOS_LOWDELAY = 0x10
IPTOS_THROUGHPUT = 0x08
IPTOS_RELIABILITY = 0x04
IPTOS_MINCOST = 0x02
IP_TTL = 2
IP_HDRINCL = 3
IP_OPTIONS = 4
IP_MULTICAST_IF = 32
IP_MULTICAST_TTL = 33
IP_MULTICAST_LOOP = 34
IP_ADD_MEMBERSHIP = 35
IP_DROP_MEMBERSHIP = 36
IP_DEFAULT_MULTICAST_TTL = 1
IP_DEFAULT_MULTICAST_LOOP = 1
IP_MAX_MEMBERSHIPS = 20
IPX_TYPE = 1
TCP_NODELAY = 1
TCP_MAXSEG = 2
SOPRI_INTERACTIVE = 0
SOPRI_NORMAL = 1
SOPRI_BACKGROUND = 2

# Included from sys/types.h

# Included from linux/types.h

# Included from linux/posix_types.h
__FD_SETSIZE = 1024
def __FDELT(d): return ((d) / __NFDBITS)


# Included from asm/posix_types.h
def __FD_ZERO(fdsetp): return \


# Included from asm/types.h

# Included from sys/bitypes.h

# Included from pthread/mit/posix.h

# Included from pthread/mit/types.h

# Included from pthread/mit/xtypes.h

# Included from pthread/mit/sys/types.h
IMPLINK_IP = 155
IMPLINK_LOWEXPER = 156
IMPLINK_HIGHEXPER = 158

# Included from linux/in.h
__SOCK_SIZE__ = 16
IN_CLASSA_NET = 0xff000000
IN_CLASSA_NSHIFT = 24
IN_CLASSA_HOST = (0xffffffff & ~IN_CLASSA_NET)
IN_CLASSA_MAX = 128
IN_CLASSB_NET = 0xffff0000
IN_CLASSB_NSHIFT = 16
IN_CLASSB_HOST = (0xffffffff & ~IN_CLASSB_NET)
IN_CLASSB_MAX = 65536
IN_CLASSC_NET = 0xffffff00
IN_CLASSC_NSHIFT = 8
IN_CLASSC_HOST = (0xffffffff & ~IN_CLASSC_NET)
def IN_MULTICAST(a): return IN_CLASSD(a)

IN_MULTICAST_NET = 0xF0000000
IN_LOOPBACKNET = 127
INADDR_LOOPBACK = 0x7f000001
INADDR_UNSPEC_GROUP = 0xe0000000
INADDR_ALLHOSTS_GROUP = 0xe0000001
INADDR_MAX_LOCAL_GROUP = 0xe00000ff

# Included from asm/byteorder.h
__LITTLE_ENDIAN = 1234

# Included from linux/config.h

# Included from linux/autoconf.h
CONFIG_MODULES = 1
CONFIG_KERNELD = 1
CONFIG_NET = 1
CONFIG_PCI = 1
CONFIG_SYSVIPC = 1
CONFIG_BINFMT_AOUT = 1
CONFIG_BINFMT_ELF = 1
CONFIG_KERNEL_ELF = 1
CONFIG_M586 = 1
CONFIG_BLK_DEV_FD = 1
CONFIG_BLK_DEV_IDE = 1
CONFIG_BLK_DEV_IDECD = 1
CONFIG_INET = 1
CONFIG_IP_NOSR = 1
CONFIG_SKB_LARGE = 1
CONFIG_SCSI = 1
CONFIG_BLK_DEV_SD = 1
CONFIG_BLK_DEV_SR = 1
CONFIG_SCSI_AHA152X = 1
CONFIG_NETDEVICES = 1
CONFIG_DUMMY_MODULE = 1
CONFIG_NET_ETHERNET = 1
CONFIG_NET_VENDOR_3COM = 1
CONFIG_EL3 = 1
CONFIG_EXT2_FS = 1
CONFIG_FAT_FS_MODULE = 1
CONFIG_MSDOS_FS_MODULE = 1
CONFIG_VFAT_FS_MODULE = 1
CONFIG_PROC_FS = 1
CONFIG_NFS_FS_MODULE = 1
CONFIG_ISO9660_FS_MODULE = 1
CONFIG_SERIAL = 1
CONFIG_MOUSE = 1
CONFIG_PSMOUSE = 1
UTS_SYSNAME = "Linux"
UTS_MACHINE = "unknown"
UTS_NODENAME = "(none)"
UTS_DOMAINNAME = "(none)"
DEF_INITSEG = 0x9000
DEF_SYSSEG = 0x1000
DEF_SETUPSEG = 0x9020
DEF_SYSSIZE = 0x7F00
NORMAL_VGA = 0xffff
EXTENDED_VGA = 0xfffe
ASK_VGA = 0xfffd
def __constant_ntohl(x): return \

def __constant_ntohs(x): return \

def __htonl(x): return __ntohl(x)

def __htons(x): return __ntohs(x)

def __constant_htonl(x): return __constant_ntohl(x)

def __constant_htons(x): return __constant_ntohs(x)

def ntohl(x): return \

def ntohs(x): return \

def htonl(x): return \

def htons(x): return \

def LOOPBACK(x): return (((x) & htonl(0xff000000)) == htonl(0x7f000000))

def MULTICAST(x): return (((x) & htonl(0xf0000000)) == htonl(0xe0000000))

