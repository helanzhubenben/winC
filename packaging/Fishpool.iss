; Fishpool per-user installer. Program and data locations are intentionally separate.
#define AppName "Fishpool"
#define AppVersion GetEnv('FISHPOOL_VERSION')
#define AppPublisher "Fishpool"
#define AppExecutable "Fishpool.exe"
#define BuildDirectory "dist\\Fishpool"

[Setup]
AppId={{EA4DBE83-2AB7-4695-9D15-79C0786C0CFB}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={localappdata}\Programs\Fishpool
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
OutputDir=dist
OutputBaseFilename=Fishpool-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
UninstallDisplayName={#AppName}

[Files]
Source: "{#BuildDirectory}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExecutable}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExecutable}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加图标："; Flags: unchecked

[Code]
var
  DataDirectoryPage: TInputDirWizardPage;
  DeleteUserData: Boolean;

function CanWriteToDirectory(const Directory: String): Boolean;
var
  ProbeFile: String;
begin
  Result := False;
  if Trim(Directory) = '' then
    Exit;

  if not ForceDirectories(Directory) then
    Exit;

  ProbeFile := AddBackslash(Directory) + 'fishpool-write-check.tmp';
  if SaveStringToFile(ProbeFile, 'ok', False) then begin
    DeleteFile(ProbeFile);
    Result := True;
  end;
end;

function ExistingDataDirectory(): String;
begin
  if not RegQueryStringValue(HKCU, 'Software\Fishpool', 'DataDirectory', Result) then
    Result := ExpandConstant('{localappdata}\Fishpool');
end;

procedure InitializeWizard();
begin
  DataDirectoryPage := CreateInputDirPage(wpSelectDir,
    '选择数据保存位置', '设置本地客户数据目录',
    'Fishpool 将在以下位置保存数据库。升级程序不会修改这里的数据；卸载时可选择保留或删除。',
    False, '');
  DataDirectoryPage.Add('客户数据目录：');
  DataDirectoryPage.Values[0] := ExistingDataDirectory();
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = wpSelectDir then begin
    if not CanWriteToDirectory(WizardDirValue) then begin
      MsgBox('所选程序安装目录没有写入权限。请使用默认目录，或选择当前用户有写入权限的文件夹。', mbError, MB_OK);
      Result := False;
    end;
  end;

  if CurPageID = DataDirectoryPage.ID then begin
    if not CanWriteToDirectory(DataDirectoryPage.Values[0]) then begin
      MsgBox('所选客户数据目录没有写入权限。请使用默认目录，或选择当前用户有写入权限的文件夹。', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then begin
    RegWriteStringValue(HKCU, 'Software\Fishpool', 'DataDirectory', DataDirectoryPage.Values[0]);
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  DataDirectory: String;
begin
  if CurUninstallStep = usUninstall then
    DeleteUserData := MsgBox('是否同时删除本地客户数据？' + #13#10 + #13#10 +
      '选择“是”将永久删除数据库，无法恢复。' + #13#10 +
      '选择“否”将保留数据，重新安装时会自动继续使用。', mbConfirmation, MB_YESNO) = IDYES;

  if (CurUninstallStep = usPostUninstall) and DeleteUserData then begin
    if RegQueryStringValue(HKCU, 'Software\Fishpool', 'DataDirectory', DataDirectory) then
      DelTree(DataDirectory, True, True, True);
    RegDeleteValue(HKCU, 'Software\Fishpool', 'DataDirectory');
  end;
end;
