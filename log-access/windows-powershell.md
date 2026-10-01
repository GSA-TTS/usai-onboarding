# Windows PowerShell: Check and Download USAi Logs

Copy and paste the blocks below into **Windows PowerShell 5.1 or PowerShell 7 on
Windows**, in order. You do not need Bash, WSL, `jq`, or Python. Each AWS command
is on one line. Copy the whole line.

Before you start, get these details from USAi:

- Your tenant code and AWS region.
- Your S3 bucket name. This is where your log files are stored.
- Your SQS queue URL. This is where notices about new files arrive.
- Your access key ID and secret access key.

Use the details **for the same log stream**: `interaction-redacted`,
`interaction-raw`, or `sec-auditlogs`. Repeat setup for each stream you can access.
If you do not have these details, contact
[usai-security@gsa.gov](mailto:usai-security@gsa.gov).

## 1. Download and install the AWS CLI

If `aws --version` already reports `aws-cli/2`, skip the installation block.
Otherwise, open **PowerShell as Administrator** and paste:

```powershell
$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
$Installer = Join-Path $env:TEMP "AWSCLIV2.msi"
Invoke-WebRequest -Uri "https://awscli.amazonaws.com/AWSCLIV2.msi" -OutFile $Installer -UseBasicParsing
$Install = Start-Process -FilePath "msiexec.exe" -ArgumentList "/i `"$Installer`" /passive /norestart" -Wait -PassThru
if ($Install.ExitCode -notin @(0, 3010)) { throw "AWS CLI installation failed with exit code $($Install.ExitCode)." }
if ($Install.ExitCode -eq 3010) { Write-Warning "Windows reports that a restart is required to finish installation." }
```

This downloads the [official AWS CLI v2 Windows installer](https://awscli.amazonaws.com/AWSCLIV2.msi)
and waits for installation to finish. If your device blocks software installation,
ask your desktop support team to install it; do not bypass your organization's
controls.

**Close PowerShell and open a new, non-administrator PowerShell window** so it
can find the newly installed `aws` command. Run the remaining steps in that
same new window:

```powershell
aws --version
```

Expected output starts with `aws-cli/2`. If `aws` is not recognized in a new
window, check with desktop support before continuing.

## 2. Set up your access

Replace the three `YOUR_...` values below with the values USAi supplied. Change
`$Stream` and `$AwsRegion` if needed. Use the actual bucket name and queue URL;
do not guess them from the tenant code.

```powershell
$ErrorActionPreference = "Stop"
$TenantCode = "YOUR_TENANT_CODE"
$Stream = "interaction-redacted"
$AwsRegion = "us-east-1"
$BucketName = "YOUR_S3_BUCKET_NAME"
$QueueUrl = "YOUR_SQS_QUEUE_URL"
$AwsProfile = "$TenantCode-$Stream-logs"
$env:AWS_PAGER = ""
```

An AWS profile saves settings under a name. The name above includes your tenant
and stream, so you can keep each stream's access keys separate.

Enter your access key ID and secret access key **only at the AWS CLI prompts**.
Do not put them in a pasted command or a support message. For the default region,
enter the value you set in `$AwsRegion`. For the default output format, enter `json`.

```powershell
aws configure --profile $AwsProfile
if ($LASTEXITCODE -ne 0) { throw "AWS CLI configuration failed. Stop here and check the error above." }
```

The AWS CLI saves the access keys in your Windows user folder. Follow your
organization's rules for storing them. Each command below uses the profile
and region you set above.

## 3. Check your AWS identity

```powershell
aws sts get-caller-identity --profile $AwsProfile --region $AwsRegion --output json
if ($LASTEXITCODE -ne 0) { throw "Identity check failed. Stop here and check your credentials." }
```

Check that `Account` and `Arn` match the reader identity supplied by USAi for
your stream. This shows which AWS identity your keys belong to. It does **not**
check whether you can read S3 files or use SQS. Stop if the identity is not the
one you expected.

## 4. Check whether log files are in S3

An S3 **object** is a stored file. Its **key** is its full name within the bucket.
List up to 20 objects to see their keys, sizes, and the dates when they were
last changed:

```powershell
aws s3api list-objects-v2 --bucket $BucketName --max-items 20 --query "Contents[].{Key:Key,SizeBytes:Size,Modified:LastModified}" --output table --profile $AwsProfile --region $AwsRegion
if ($LASTEXITCODE -ne 0) { throw "S3 listing failed. Stop here and check the error above." }
```

- Object rows mean files exist and you can list them. Downloading a file in the
  next step checks whether you can also read its contents.
- This shows up to 20 objects sorted by key, **not the 20 newest files**.
  Pick a log file, not a folder marker whose key ends in `/`.
- An empty result with no error means AWS returned no objects for this bucket.
  `AccessDenied` means AWS did not allow the request. It does not mean the bucket
  is empty.

**Optional, for interaction logs with the documented `yyyy/MM/dd/` layout:** list
files whose keys start with today's date in UTC. Do not assume security-audit
logs use this layout.

```powershell
$DatePrefix = (Get-Date).ToUniversalTime().ToString("yyyy/MM/dd/")
aws s3 ls "s3://$BucketName/$DatePrefix" --recursive --profile $AwsProfile --region $AwsRegion
if ($LASTEXITCODE -ne 0) { throw "S3 date-prefix listing failed. Check the error above." }
```

No files under today's date does not mean the whole bucket is empty. Check the
bucket sample above and use the actual keys it returns.

## 5. Download one log file

Copy the full `Key` from a listing above. Paste it at the prompt below, without
surrounding quotes or `s3://bucket-name/`. Use the key exactly as listed; do not
URL-decode keys copied from an S3 listing.

This saves one file in `USAi-logs` under your Windows user folder, with a unique
name so it does not overwrite an earlier download. Logs may contain personal
information; use an approved device and storage location.

```powershell
$ObjectKey = Read-Host "Paste the full S3 object key from the listing"
if ([string]::IsNullOrWhiteSpace($ObjectKey) -or $ObjectKey.EndsWith("/")) { throw "Enter a file key, not an empty value or a folder prefix." }
$DownloadDirectory = Join-Path $HOME "USAi-logs"
New-Item -ItemType Directory -Path $DownloadDirectory -Force | Out-Null
$Suffix = if ($ObjectKey.EndsWith(".gz")) { ".json.gz" } else { ".json" }
$LocalFile = Join-Path $DownloadDirectory ("log-" + [guid]::NewGuid().ToString("N") + $Suffix)
aws s3 cp "s3://$BucketName/$ObjectKey" $LocalFile --profile $AwsProfile --region $AwsRegion
if ($LASTEXITCODE -ne 0) { throw "Log download failed. Do not treat a partial local file as a successful download." }
Get-Item -LiteralPath $LocalFile | Select-Object -Property @("FullName", "Length")
```

The `download:` message and local file details show which file was saved. If
listing works but downloading returns `AccessDenied`, send the USAi team the
failed operation, error, bucket name, and object key. Do not send credentials
or log contents.

Optionally preview an **uncompressed** file locally:

```powershell
if ($LocalFile.EndsWith(".gz")) {
    Write-Host "This file is gzip-compressed. Extract it with an approved gzip-capable tool before viewing it."
} else {
    Get-Content -LiteralPath $LocalFile -TotalCount 5
}
```

Interaction files contain NDJSON (one JSON event per line). A security-audit
object contains a single JSON record. See [schemas and examples](examples/README.md).

## 6. Check the queue without removing messages

```powershell
aws sqs get-queue-attributes --queue-url $QueueUrl --attribute-names ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible --profile $AwsProfile --region $AwsRegion --output json
if ($LASTEXITCODE -ne 0) { throw "Queue check failed. Check the queue URL, profile, region, and GetQueueAttributes permission with USAi." }
```

- `ApproximateNumberOfMessages`: notifications available to receive.
- `ApproximateNumberOfMessagesNotVisible`: notifications another program has
  received but has not yet deleted or returned to the queue.
- These counts are estimates. **Zero notifications does not mean no log files
  exist in S3.** Another program may already have processed the notifications.

This check uses `GetQueueAttributes`. It does not receive, hide, or delete
messages. Your log collection service can still receive those notifications.
If AWS denies this queue check, you may still be able to download files from S3.
Ask USAi to check your queue access separately.

## What these checks tell you

| Check | What a successful result tells you |
|---|---|
| `aws --version` | AWS CLI is installed and available in this PowerShell window |
| `get-caller-identity` | Your access keys belong to the displayed identity |
| S3 listing with object rows | Objects exist and your identity can list them |
| S3 download | Your identity can read that specific object and save it locally |
| Queue attributes | Your identity can check the estimated number of notifications |

These checks show whether you can access and download files. They do not show
whether your security monitoring tool has loaded the logs. To collect logs
automatically, see the [full log-access guide](log-access-guide.md#automated-access-python-script).
