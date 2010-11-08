@ECHO OFF

if exist ..\..\..\..\PCbuild\python.exe set PYTHON="..\..\..\..\PCbuild\python.exe"
if exist ..\..\..\..\PCbuild\python_d.exe set PYTHON="..\..\..\..\PCbuild\python_d.exe"
if exist ..\..\..\..\PCbuild\amd64\python.exe set PYTHON="..\..\..\..\PCbuild\amd64\python.exe"
if exist ..\..\..\..\PCbuild\amd64\python_d.exe set PYTHON="..\..\..\..\PCbuild\amd64\python_d.exe"

if not exist runtest.exe goto error

call gettests.bat

echo.
echo Running official tests ...
echo.
runtest.exe --all official.decTest

echo.
echo Running additional tests ...
echo.
runtest.exe --all additional.decTest

echo.
echo Running coverage tests ...
echo.
cov.exe
test_transpose.exe
fntcov.exe

echo.
echo Running long tests ...
echo.
ppro_mulmod.exe
if exist mpd_mpz_add.exe mpd_mpz_add.exe -q
if exist mpd_mpz_sub.exe mpd_mpz_sub.exe -q
if exist mpd_mpz_mul.exe mpd_mpz_mul.exe -q
if exist mpd_mpz_divmod.exe mpd_mpz_divmod.exe -q
karatsuba_fnt.exe -q
karatsuba_fnt2.exe -q


echo.
echo Running locale and format tests ...
echo.
%PYTHON% ..\python\genrandlocale.py | runtest.exe -
%PYTHON% ..\python\genrandformat.py | runtest.exe -
%PYTHON% ..\python\genlocale.py | runtest.exe -

goto finish


:error
echo.
echo error: the tests must be built first
echo.

:finish


