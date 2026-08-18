
; PairsStrat.iss
[Setup]
AppName=Pairs Stratification
AppVersion=1.07
AppPublisher="Steve Pomeroy"
DefaultDirName={sd}\PairsStrat
DefaultGroupName=PairsStratification
OutputBaseFilename=PairsStrat-Setup
Compression=lzma
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
DisableDirPage=no
SourceDir=..\
OutputDir=installer_output
SetupIconFile=resources\PairsStratificationAppIco.ico
UninstallDisplayIcon={app}\PairsStrat.exe
VersionInfoCompany=Steve Pomeroy
VersionInfoDescription=Paits Stratification Installer
VersionInfoCopyright=Copyright © 2026 Steve Pomeroy
VersionInfoVersion=1.07
VersionInfoProductName=Pairs Stratification
VersionInfoProductVersion=1.07

[Files]
Source:"dist\PairsStrat.exe"; DestDir:"{app}"; Flags: ignoreversion
Source:"dist\PairsStrat\config.json"; DestDir:"{app}"; Flags: onlyifdoesntexist
Source:"webpage\SingleFileTmpl.html"; DestDir:"{app}"; Flags: ignoreversion
Source:"webpage\TinyFileTmpl.html"; DestDir:"{app}"; Flags: ignoreversion
Source:"webpage\webpage.css"; DestDir:"{app}"; Flags: ignoreversion
Source:"webpage\webpage.js"; DestDir:"{app}"; Flags: ignoreversion
Source:"readme.txt"; DestDir:"{app}"; Flags: ignoreversion
Source:"dist\PairsStrat\_internal\*"; DestDir:"{app}\_internal"; Flags: ignoreversion recursesubdirs
Source: "resources\PairsStratificationAppIco.ico"; DestDir: "{app}\resources"
Source: "resources\PairsStratificationIco.ico"; DestDir: "{app}\resources"
Source: "resources\PairsStratificationAbout.png"; DestDir: "{app}\resources"
Source: "resources\PairsStratification.bmp"; Flags: dontcopy

[Icons]
Name:"{group}\Pairs Stratification"; Filename:"{app}\PairsStrat.exe"; IconFilename: "{app}\resources\PairsStratificationAppIco.ico"
Name:"{userdesktop}\Stratification"; Filename:"{app}\PairsStrat.exe"; IconFilename: "{app}\resources\PairsStratificationIco.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"

[Run]
Filename:"{app}\PairsStrat.exe"; Description:"Launch Pairs Stratification"; Flags: nowait postinstall skipifsilent

[Code]
var
  IntroPage: TWizardPage;
  IntroImage: TBitmapImage;

procedure InitializeWizard();
begin
  ExtractTemporaryFile('PairsStratification.bmp');
  IntroPage := CreateCustomPage(
    wpWelcome,
    'Welcome to the Pairs Stratification Installer',
    'The installer will guide you through the setup process.'
  );

  IntroImage := TBitmapImage.Create(IntroPage);
  IntroImage.Parent := IntroPage.Surface;

  IntroImage.Bitmap.LoadFromFile(ExpandConstant('{tmp}\PairsStratification.bmp'));

  IntroImage.Left := 70;
  IntroImage.Top := 0;
  IntroImage.Width := 360;
  IntroImage.Height := 200;

  with TLabel.Create(IntroPage) do
  begin
    Parent := IntroPage.Surface;
    Caption := '         Welcome to the Pairs Stratification Program.' + #13#10 + #13#10 +
               'This installer will set up the application on your system.' + #13#10 + #13#10 +
               '                          Click Next to continue.';
    Left := 115;
    Top := 200;
    Width := IntroPage.SurfaceWidth;
    Height := 50;
    WordWrap := True;
  end;
end;