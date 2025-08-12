rem mkdir tmp
for /f "tokens=1,* delims=|" %%i in ('git log -n 10 --pretty^=format:"%%H|%%cd" --date=iso -- swimmeterApp/app/release/app-release.aab') do (
    set "datetime=%%j"
    setlocal enabledelayedexpansion
    rem Remove timezone by splitting at space and keeping first two parts
    for /f "tokens=1,2 delims= " %%a in ("!datetime!") do (
        set "cleaned=%%a_%%b"
        set "cleaned=!cleaned::=_!"
        set "cleaned=!cleaned::=_!"
        git show %%i:swimmeterApp/app/release/app-release.aab > tmp\app-release_!cleaned!.aab
    )
    endlocal
)