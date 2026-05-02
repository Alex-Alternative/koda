{ installer/system_check.iss
  --------------------------
  Pascal mirror of system_check.classify(). Used during the Inno wizard
  pages BEFORE Koda.exe is extracted. Determines tier so the soft-warn
  / Power Mode pages can be shown ahead of the file extraction step.

  After extraction, koda.iss runs Koda.exe --detect-hardware --json for
  the authoritative classification (which can verify CUDA runtime
  usability, something Pascal cannot).

  Constants come from installer/thresholds.iss (auto-generated).

  IMPORTANT: This file is #include'd by koda.iss INSIDE the [Code]
  section. It must not contain its own [Code] header.
}

{ Win32 imports }
function GlobalMemoryStatusEx(lpBuffer: TMemoryStatusEx): BOOL;
  external 'GlobalMemoryStatusEx@kernel32.dll stdcall';

type
  TMemoryStatusEx = record
    dwLength: DWORD;
    dwMemoryLoad: DWORD;
    ullTotalPhys: Int64;
    ullAvailPhys: Int64;
    ullTotalPageFile: Int64;
    ullAvailPageFile: Int64;
    ullTotalVirtual: Int64;
    ullAvailVirtual: Int64;
    ullAvailExtendedVirtual: Int64;
  end;

{ Detection helpers }

function DetectRamGB: Double;
var
  Mem: TMemoryStatusEx;
begin
  Mem.dwLength := SizeOf(Mem);
  if GlobalMemoryStatusEx(Mem) then
    Result := Mem.ullTotalPhys / (1024 * 1024 * 1024)
  else
    Result := -1;  { detection failure }
end;

function DetectCores: Integer;
var
  SysInfo: TSystemInfo;
begin
  GetSystemInfo(SysInfo);
  Result := SysInfo.dwNumberOfProcessors;
end;

function DetectFreeDiskGB: Double;
var
  FreeBytes: Cardinal;
begin
  { GetSpaceOnDisk returns free MB; convert to GB }
  if GetSpaceOnDisk(ExpandConstant('{sd}\'), True, FreeBytes, FreeBytes) then
    Result := FreeBytes / 1024
  else
    Result := -1;
end;

function DetectWinBuild: Integer;
var
  WinVer: TWindowsVersion;
begin
  GetWindowsVersionEx(WinVer);
  Result := WinVer.Build;
end;

function DetectCpuName: String;
begin
  if not RegQueryStringValue(
    HKEY_LOCAL_MACHINE,
    'HARDWARE\DESCRIPTION\System\CentralProcessor\0',
    'ProcessorNameString',
    Result
  ) then
    Result := '';
end;

function DetectNvidiaGpuPresent: Boolean;
var
  ResultCode: Integer;
  TempPath: String;
begin
  { Run nvidia-smi, redirect output to a temp file. If it exists and is
    non-empty, NVIDIA GPU is present. }
  TempPath := ExpandConstant('{tmp}\nvidia_check.txt');
  Exec(
    ExpandConstant('{cmd}'),
    '/c "nvidia-smi --query-gpu=name --format=csv,noheader > "' + TempPath + '" 2>NUL"',
    '', SW_HIDE, ewWaitUntilTerminated, ResultCode
  );
  Result := FileExists(TempPath) and (FileSize(TempPath) > 5);
end;

function IsLowPowerCpu(const CpuName: String): Boolean;
var
  i: Integer;
  NameLower: String;
begin
  NameLower := Lowercase(CpuName);
  Result := False;
  for i := 0 to CPU_LOW_POWER_PATTERN_COUNT - 1 do
    if Pos(CPU_LOW_POWER_PATTERNS[i], NameLower) > 0 then
    begin
      Result := True;
      Exit;
    end;
end;

{ Tier classifier — returns one of: 'BLOCKED', 'MINIMUM', 'RECOMMENDED', 'POWER' }

function ClassifyTier: String;
var
  RamGB, FreeDiskGB: Double;
  Cores, WinBuild: Integer;
  CpuName: String;
  HasNvidia, IsLowPower: Boolean;
begin
  RamGB := DetectRamGB;
  Cores := DetectCores;
  FreeDiskGB := DetectFreeDiskGB;
  WinBuild := DetectWinBuild;
  CpuName := DetectCpuName;
  HasNvidia := DetectNvidiaGpuPresent;
  IsLowPower := IsLowPowerCpu(CpuName);

  { BLOCKED checks }
  if (RamGB > 0) and (RamGB < {#RAM_BLOCKED_MIN_GB}) then begin
    Result := 'BLOCKED';
    Exit;
  end;
  if (FreeDiskGB > 0) and (FreeDiskGB < {#DISK_BLOCKED_MIN_FREE_GB}) then begin
    Result := 'BLOCKED';
    Exit;
  end;
  if (WinBuild > 0) and (WinBuild < {#WIN_BLOCKED_MIN_BUILD}) then begin
    Result := 'BLOCKED';
    Exit;
  end;

  { POWER tier — Pascal cannot verify CUDA runtime, so we treat NVIDIA-presence
    as POWER-eligible. The post-extract Koda.exe --detect-hardware call will
    correct to RECOMMENDED if CUDA runtime isn't usable. }
  if HasNvidia then begin
    Result := 'POWER';
    Exit;
  end;

  { MINIMUM checks }
  if (Cores < {#CORES_MIN_RECOMMENDED}) or
     (RamGB < {#RAM_MIN_RECOMMENDED_GB}) or
     IsLowPower then begin
    Result := 'MINIMUM';
    Exit;
  end;

  Result := 'RECOMMENDED';
end;
