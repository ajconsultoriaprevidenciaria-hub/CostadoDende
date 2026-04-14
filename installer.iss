#define MyAppName "Costa do Dende"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Costa do Dende"
#define MyAppExeName "CostadoDende.exe"
#define MyAppSourceDir "c:\Users\usuario\Desktop\projeto\CostadoDende\CostadoDende\dist\CostadoDende"
#define MyAppOutputDir "c:\Users\usuario\Desktop\projeto\CostadoDende\CostadoDende\installer"

[Setup]
AppId={{B29D3E4A-6BF0-4CE4-84B2-5A2D44D5A2F8}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir={#MyAppOutputDir}
OutputBaseFilename=CostadoDende-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na area de trabalho"; GroupDescription: "Atalhos adicionais:"; Flags: unchecked

[Files]
Source: "{#MyAppSourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Executar {#MyAppName}"; Flags: nowait postinstall skipifsilent