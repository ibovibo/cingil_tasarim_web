import shutil, os
src = r'c:\Users\Asus\Desktop\cingilweb_full\www.ruyaajansorganizasyon.com\images'
dst = r'c:\Users\Asus\Desktop\cingilweb\assets\images'
print('src exists', os.path.exists(src))
if os.path.exists(src):
    shutil.copytree(src, dst, dirs_exist_ok=True)
    print('images copied to', dst)
else:
    print('source images not found:', src)
