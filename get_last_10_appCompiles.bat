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


rem java -jar bundletool-all-1.12.1.jar  build-apks --bundle=app-release_2024-07-19_13_35_51.aab --output=my_app.apks --mode=universal
rem does not work, can't install it without the keystore... Need to copy this one from somewhere else...