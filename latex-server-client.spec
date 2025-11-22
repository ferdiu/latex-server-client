Name:           latex-server-client
Version:        2.0.0
Release:        1%{?dist}
Summary:        A watchdog client for latex-server

License:        MIT
URL:            https://github.com/ferdiu/latex-server-client
Source0:        %{url}/archive/v%{version}/latex-server-client-%{version}.tar.gz

BuildArch:      noarch

# Python build deps
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-requests
BuildRequires:  python3-watchdog
BuildRequires:  python3-pathspec

# Runtime deps
Requires:       python3
Requires:       python3-requests >= 2.31.0
Requires:       python3-watchdog >= 3.0.0
Requires:       python3-pathspec >= 0.11.0

# Recommendations for local compilation
Recommends:     python3-latex-server

# The executable name will be different from the package name
Provides:       latex-watch


%global _description %{expand:
A watchdog based client to run in your LaTeX project directory
to automatically compiles your document whenever files change.
}

%description %_description



####################################
# MAIN PYTHON PACKAGE
####################################

%package -n python3-latex-server-client
Summary: %{summary}
%description -n python3-latex-server-client %_description



####################################
# PREP
####################################

%prep
%autosetup -p1 -n latex-server-client-%{version}
%generate_buildrequires
%pyproject_buildrequires



####################################
# BUILD
####################################

%build
%pyproject_wheel



####################################
# INSTALL
####################################

%install
%pyproject_install
%pyproject_save_files -l latex_server_client


####################################
# CHECK
####################################

%check
%pyproject_check_import


####################################
# FILES
####################################

%files -n python3-latex-server-client -f %{pyproject_files}
%{_bindir}/latex-watch
%doc README.md


%changelog
* Sat Nov 22 2025 Federico Manzella <ferdiu.manzella@gmail.com> - 2.0.0-1
- Update protocol to support binary files

* Sat Nov 22 2025 Federico Manzella <ferdiu.manzella@gmail.com> - 1.0.1-1
- First release