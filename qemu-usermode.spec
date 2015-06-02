# Target architectures to build emulators of
%define target_list aarch64 arm mipsel

Name:       qemu-usermode
Summary:    Universal CPU emulator
Version:    2.1.0
Release:    1
Group:      System/Emulators/PC
License:    GPLv2
ExclusiveArch:  %{ix86}
URL:        https://launchpad.net/qemu-linaro/
Source0:    qemu-%{version}.tar.bz2
Source1:    qemu-binfmt-conf.sh
Patch0:     fix-glibc-install-locales.patch
Patch1:     mips-support.patch
Patch2:     0038-linux-user-fix-segfault-deadlock.pa.patch
Patch3:     0023-target-arm-linux-user-no-tb_flush-o.patch
Patch4:     0024-linux-user-lock-tcg.patch
Patch5:     0025-linux-user-Run-multi-threaded-code-on-one-core.patch
Patch6:     0026-linux-user-lock-tb-flushing-too.patch
Patch7:     fix-strex.patch
BuildRequires:  pkgconfig(ext2fs)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  bison
BuildRequires:  curl-devel
BuildRequires:  zlib-static
BuildRequires:  glibc-static
BuildRequires:  python-devel
BuildRequires:  glib2-static
BuildRequires:  pcre-static
Requires: %{name}-common = %{version}

%description
QEMU is an extremely well-performing CPU emulator that allows you to choose between simulating an entire system and running userspace binaries for different architectures under your native operating system. It currently emulates x86, ARM, PowerPC and SPARC CPUs as well as PC and PowerMac systems.


%prep
%setup -q -n qemu-%{version}

# fix-glibc-install-locales.patch
%patch0 -p1
# mips-support.patch
%patch1 -p1
# 0038-linux-user-fix-segfault-deadlock.pa.patch
%patch2 -p1
# 0023-target-arm-linux-user-no-tb_flush-o.patch
%patch3 -p1
# 0024-linux-user-lock-tcg.patch
%patch4 -p1
# 0025-linux-user-Run-multi-threaded-code-on-one-core.patch
%patch5 -p1
# 0026-linux-user-lock-tb-flushing-too.patch
%patch6 -p1
# fix-strex.patch
%patch7 -p1

%build
CFLAGS=`echo $CFLAGS | sed 's|-fno-omit-frame-pointer||g'` ; export CFLAGS ;
CFLAGS=`echo $CFLAGS | sed 's|-O2|-O|g'` ; export CFLAGS ;

CONFIGURE_FLAGS="--prefix=/usr \
    --sysconfdir=%_sysconfdir \
    --interp-prefix=/usr/share/qemu/qemu-i386 \
    --disable-system \
    --enable-linux-user \
    --enable-guest-base \
    --disable-werror \
    --target-list=$((for target in %{target_list}; do echo -n ${target}-linux-user,; done) | sed -e 's/,$//')"

for mode in static dynamic; do
    mkdir build-$mode
    cd build-$mode
    if [ $mode = static ]; then
        ../configure --static $CONFIGURE_FLAGS
    else
        ../configure $CONFIGURE_FLAGS
    fi
    make %{?jobs:-j%jobs}
    cd ..
done

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/usr/sbin
install -m 755 %{SOURCE1} $RPM_BUILD_ROOT/usr/sbin

for mode in static dynamic; do
    cd build-$mode
    %make_install
    for target in %{target_list}; do
        mv %{buildroot}%{_bindir}/qemu-${target} %{buildroot}%{_bindir}/qemu-${target}-${mode}
    done
    cd ..
done

rm -f $RPM_BUILD_ROOT/usr/share/qemu/openbios-ppc
rm -f $RPM_BUILD_ROOT/usr/share/qemu/openbios-sparc32
rm -f $RPM_BUILD_ROOT/usr/share/qemu/openbios-sparc64
rm -f $RPM_BUILD_ROOT/usr/libexec/qemu-bridge-helper
rm -rf $RPM_BUILD_ROOT/etc
rm -rf $RPM_BUILD_ROOT/%{_datadir}


%files
%defattr(-,root,root,-)
%{_bindir}/qemu-*-dynamic
%{_sbindir}/qemu-binfmt-conf.sh

%package common
Summary:  Universal CPU emulator (common utilities)
Group:      System/Emulators/PC

%description common
This package provides common qemu utilities.

%files common
%defattr(-,root,root,-)
%{_bindir}/qemu-ga
%{_bindir}/qemu-img
%{_bindir}/qemu-io
%{_bindir}/qemu-nbd

%package static
Summary:  Universal CPU emulator (static userspace emulators)
Group:      System/Emulators/PC
Requires: %{name}-common = %{version}

%description static
This package provides static builds of userspace CPU emulators.

%files static
%defattr(-,root,root,-)
%{_bindir}/qemu-*-static
