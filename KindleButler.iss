#define MyAppName "KindleButler"
#define MyAppVersion "0.1"
#define MyAppPublisher "Paweł Jastrzębski"
#define MyAppURL "https://github.com/AcidWeb/KindleButler"
#define MyAppExeName "KindleButler.exe"

[Setup]
AppId={{5A247DA9-157C-4BCC-9C42-0F010A616378}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppCopyright=Copyright (C) 2014 Paweł Jastrzębski
DefaultDirName={pf}\{#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE.txt
OutputBaseFilename=KindleButler_win_{#MyAppVersion}
SetupIconFile=Assets\KindleButler.ico
SolidCompression=yes
ShowLanguageDialog=no
LanguageDetectionMethod=none
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
ChangesAssociations=yes
SignTool=SignTool /d $q{#MyAppName}$q /du $q{#MyAppURL}$q $f

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "dist\tcl\*"; DestDir: "{app}\tcl\"; Flags: ignoreversion;
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion;
Source: "dist\*.dll"; DestDir: "{app}"; Flags: ignoreversion;
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "KindleButler.ini"; DestDir: "{app}"; Flags: ignoreversion
Source: "Assets\vcredist_x86.exe"; DestDir: "{tmp}"; Flags: ignoreversion deleteafterinstall;

[Run]
Filename: "{tmp}\vcredist_x86.exe"; Parameters: "/passive /Q:a /c:""msiexec /qb /i vcredist.msi"" "; StatusMsg: "Installing Microsoft Visual C++ 2010 Redistributable Package...";

[Registry]
Root: HKCR; Subkey: ".mobi"; ValueType: string; ValueName: ""; ValueData: "KindleButler"; Flags: uninsdeletevalue
Root: HKCR; Subkey: ".azw"; ValueType: string; ValueName: ""; ValueData: "KindleButler"; Flags: uninsdeletevalue
Root: HKCR; Subkey: ".azw3"; ValueType: string; ValueName: ""; ValueData: "KindleButler"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "KindleButler"; ValueType: string; ValueName: ""; ValueData: ""; Flags: uninsdeletevalue
Root: HKCR; Subkey: "KindleButler\shell"; ValueType: string; ValueName: ""; ValueData: "open";
Root: HKCR; Subkey: "KindleButler\shell\open"; ValueType: string; ValueName: ""; ValueData: "Send to Kindle";
Root: HKCR; Subkey: "KindleButler\shell\customcover"; ValueType: string; ValueName: ""; ValueData: "Send to Kindle - Custom cover";
Root: HKCR; Subkey: "KindleButler\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKCR; Subkey: "KindleButler\shell\customcover\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" -c ""%1"""