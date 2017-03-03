%{?_javapackages_macros:%_javapackages_macros}

%define debug_package %{nil}

%define commit fb5ed5e378f64d59e54a92d52c865c383a69e314
%define shortcommit %(c=%{commit}; echo ${c:0:7})

#
# NOTE: G.722 patents have expired
#       https://en.wikipedia.org/wiki/G.722#Licensing
#

Summary:	Jitsi dependencies released under LGPL license
Name:		jitsi-lgpl-dependencies
Version:	0
Release:	0
License:	LGPLv2
Group:	 	Development/Java
Url:		https://github.com/jitsi/%{name}
Source0:	https://github.com/jitsi/%{name}/archive/%{commit}/%{name}-%{commit}.zip

BuildRequires:	ant
BuildRequires:	cpptasks
BuildRequires:	javapackages-local
BuildRequires:	maven-local
BuildRequires:	mvn(net.java.dev.jna:jna)
BuildRequires:	mvn(org.apache.felix:maven-bundle-plugin)
# natives
#   g722
BuildRequires:	pkgconfig(libv4l2)
BuildRequires:	pkgconfig(spandsp)

# natives
Requires:	%{_lib}spandsp2

%description
Jitsi dependencies released under LGPL license.

%files -f .mfiles

#----------------------------------------------------------------------------

%package javadoc
Summary:	Javadoc for %{name}
BuildArch:	noarch

%description javadoc
API documentation for %{name}.

%files javadoc -f .mfiles-javadoc

#----------------------------------------------------------------------------

%prep
%setup -q -n %{name}-%{commit}
# Delete prebuild JARs and libs
find . -type f -name \*.jar -delete
find . -type f -name \*.class -delete
find . -type f -name \*.dll -delete
find . -type f -name \*.jnilib -delete
find . -type f -name lib\*.so\* -delete

# Fix classpath
ln -fs `build-classpath ant/cpptasks` ./lib/installer-exclude/cpptasks.jar

# Unbundle native libs for other SO and arch
sed -i -e '{	/darwin/d
		/linux-x86-64/d
		/win32-x86/d
		/win32-x86-64/d
		s|linux-x86|linux-@arch@|g
		s|processor=x86|processor=@arch@|g
		s|@arch@,|@arch@|g
	    }' pom.xml

# use properly arch
%ifarch %{x?86}
sed -i -e '{	s|linux-@arch@|linux-x86|g
		s|processor=@arch@|processor=x86|g
	   }' pom.xml
%endif

%ifarch x86_64
sed -i -e '{	s|linux-@arch@|linux-x86-64|g
		s|processor=@arch@|processor=x86-64|g
	   }' pom.xml
%endif

# Switch to JDK 8
%pom_add_plugin :maven-compiler-plugin . "
<configuration>
	<source>1.8</source>
	<target>1.8</target>
</configuration>"

# Remove jitsi-universe parent
%pom_remove_parent .

# Add groupId
%pom_xpath_inject "pom:project" "<groupId>org.jitsi</groupId>" .

# Fix missing version warnings
%pom_xpath_inject "pom:plugin[pom:artifactId[./text()='maven-bundle-plugin']]" "
	<version>any</version>" .

# Fix resources path
%pom_xpath_replace "pom:resources/pom:resource/pom:directory" "
	<directory>src/main/resources</directory>" .

# Add an OSGi compilant MANIFEST.MF
%pom_xpath_inject "pom:plugin[pom:artifactId[./text()='maven-bundle-plugin']]" "
	<extensions>true</extensions>"

# Add 'Export-Package' in MANIFEST.MF
%pom_xpath_remove "pom:Export-Package"

# Fix JAR name
%mvn_file :%{name} %{name}-%{version} %{name}

%build
# g722
%ant -v g722

# remove history.xml
rm -f src/main/resources/*/history.xml

# java
%mvn_build -- -Dproject.build.sourceEncoding=UTF-8

%install
%mvn_install

