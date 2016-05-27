Name: %{name}
Version: %{version}
Release: %{revision}
BuildArch: %{architecture}
Group: Development Tools

Vendor: %{vendor}
Packager: %{vendor} <%{email}>

Summary: NVIDIA Docker container tools
URL: https://github.com/NVIDIA/nvidia-docker
License: BSD

Source0: %{name}_%{version}_%{architecture}.tar.xz
Source1: %{name}.service
Source2: LICENSE

%{?systemd_requires}
BuildRequires: systemd
Requires: docker-engine

%define nvidia_docker_user %{name}
%define nvidia_docker_driver %{name}
%define nvidia_docker_root /var/lib/nvidia-docker

%description
NVIDIA Docker provides utilities to extend the Docker CLI allowing users
to build and run GPU applications as lightweight containers.

%prep
%autosetup -n %{name}
cp %{SOURCE1} %{SOURCE2} .

%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{nvidia_docker_root}
install -m 755 -t %{buildroot}%{_bindir} nvidia-docker
install -m 755 -t %{buildroot}%{_bindir} nvidia-docker-plugin
install -m 644 -t %{buildroot}%{_unitdir} %{name}.service

%files
%license LICENSE
%dir %{nvidia_docker_root}
%{_bindir}/*
%{_unitdir}/*

%post
if [ $1 -eq 1 ]; then
    id -u %{nvidia_docker_user} >/dev/null 2>&1 || \
    useradd -r -M -d %{nvidia_docker_root} -s /usr/sbin/nologin -c "NVIDIA Docker plugin" %{nvidia_docker_user}
    chown %{nvidia_docker_user}: %{nvidia_docker_root}
fi
setcap cap_fowner+pe %{_bindir}/nvidia-docker-plugin
%systemd_post %{name}

%preun
if [ $1 -eq 0 ]; then
    docker volume ls | awk -v drv=%{nvidia_docker_driver} '{if ($1 == drv) print $2}' | xargs -r docker volume rm || exit 1
    find %{nvidia_docker_root} ! -wholename %{nvidia_docker_root} -type d -empty -delete
fi
%systemd_preun %{name}

%postun
if [ $1 -eq 0 ]; then
    id -u %{nvidia_docker_user} >/dev/null 2>&1 && \
    userdel %{nvidia_docker_user}
fi
%systemd_postun_with_restart %{name}

%changelog
* Tue May 03 2016 NVIDIA CORPORATION <digits@nvidia.com> 1.0.0~rc-1
- Add /docker/cli/json RestAPI endpoint (Closes: #39, #91)
- Fix support for Docker 1.9 (Closes: #83)
- Handle gracefully devices unsupported by NVML (Closes: #40)
- Improve error reporting
- Support for Docker 1.11 (Closes: #89, #84, #77, #73)
- Add NVIDIA Docker version output
- Improve init scripts and add support for systemd
- Query CPU affinity through sysfs instead of NVML (Closes: #65)
- Load UVM before anything else

* Mon Mar 28 2016 NVIDIA CORPORATION <digits@nvidia.com> 1.0.0~beta.3-1
- Remove driver hard dependency (NVML)
- Improve error handling and REST API output
- Support for 364 drivers
- Preventive removal of the plugin socket

* Mon Mar 07 2016 NVIDIA CORPORATION <digits@nvidia.com> 1.0.0~beta.2-1
- Support for Docker 1.10 (Closes: #46)
- Support for Docker plugin API v1.2
- Support for 361 drivers
- Add copy strategy for cross-device volumes (Closes: #47)

* Mon Feb 08 2016 NVIDIA CORPORATION <digits@nvidia.com> 1.0.0~beta-1
- Initial release (Closes: #33)