import os
import json
import glob
import shutil
import subprocess


# matlab_dir = "../datajoint-matlab/"
# python_dir = "../datajoint-python/"



if not os.path.exists('build1'):
    os.makedirs('build1')
    subprocess.Popen(
        ["git", "clone", "git@github.com:mahos/testDocMain.git", "datajoint-docs"], cwd="build1").wait()
    
    subprocess.Popen(
        ["git", "clone", "git@github.com:mahos/testDocMatlab.git", "datajoint-matlab"], cwd="build1").wait()
    
    subprocess.Popen(
        ["git", "clone", "git@github.com:mahos/testDocPython.git", "datajoint-python"], cwd="build1").wait()
    

# srcComm = "build1/datajoint-docs/contents"
# srcMat = "build1/datajoint-matlab/docs/"
# srcPy = "build1/datajoint-python/docs/"

def create_build_folders(lang): 
    # raw_tags = subprocess.Popen(["git", "tag"], cwd="build1/datajoint-" + lang, stdout=subprocess.PIPE).communicate()[0].decode("utf-8").split()
    # tags1 = {}
    # tags1[lang] = raw_tags
    # print(tags1)

    lv = open("build_versions.json")
    buildver = lv.read()
    tags = json.loads(buildver)
    lv.close()

    # tags2 = {"python": [
    #                     # "v0.9.0",
    #                     "v0.9.1"],
    #          "matlab": [
    #                     # "v3.2.0",
    #                     # "v3.2.1",
    #                     "v3.2.2"]
    #          }
    # for tag in tags2[lang]:
    for tag in tags[lang]:
        subprocess.Popen(["git", "checkout", tag],
                         cwd="build1/datajoint-" + lang, stdout=subprocess.PIPE).wait()
        dsrc_lang2 = "build1/datajoint-" + lang + "/docs"
        dst_build_folder = "build1/" + lang + "-" + tag 
        dst_main = dst_build_folder + "/contents"
        dst_temp = dst_main + "/comm"

        if os.path.exists(dst_build_folder):
            shutil.rmtree(dst_build_folder)

        # copy over the lang source doc contents into the build folder 
        shutil.copytree(dsrc_lang2, dst_main)

        # grab which version of the common folder the lang doc needs to be merged with
        cv = open(dsrc_lang2 + "/_version_common.json")
        v = cv.read() # expected in this format { "comm_version" : "v0.0.0"}
        version_info = json.loads(v)
        cv.close
        subprocess.Popen(["git", "checkout", version_info['comm_version']],
                         cwd="build1/datajoint-docs", stdout=subprocess.PIPE).wait()
        dsrc_comm2 = "build1/datajoint-docs/contents"
        # copy over the cmmon source doc contents into the build folder 
        shutil.copytree(dsrc_comm2, dst_temp)

        # copying and merging all of the folders from lang-specific repo to build folder
        for root, dirs, filename in os.walk(dst_temp):
            # print("root: " + root),
            # print("dirs"),
            # print(dirs),
            # print("filenames"),
            # print(filename),
            # print("+++++++++++++++++++++++++++++++++"),
            for f in filename:
                fullpath = os.path.join(root, f)
                print(fullpath)
                if len(dirs) == 0:
                    root_path, new_path = root.split("comm/")
                    shutil.copy2(fullpath, root_path + new_path)
            print("-------------------------------")

        # copying the toc tree and the config files
        shutil.copy2(dst_temp + "/" + "index.rst", dst_main + "/" + "index.rst")

        # removing the temporary comm folder because that shouldn't get build
        shutil.rmtree(dst_temp)

        # copy the datajoint_theme folder, conf.py and makefile for individual lang-ver folder building
        shutil.copytree("datajoint_theme", dst_build_folder + "/datajoint_theme")
        shutil.copy2("Makefile", dst_build_folder + "/Makefile")
        shutil.copy2("contents/conf.py", dst_build_folder + "/contents/" + "conf.py")

        # JIC add current_version <p> tag into the datajoint_theme folder 
        f = open(dst_build_folder + '/datajoint_theme/this_version.html', 'w+')
        f.write('<p>' + lang + "-" + tag + '</p>') 
        f.close()

        # build individual lang-ver folder
        # subprocess.Popen(["make", "site"], cwd=dst_build_folder).wait()

create_build_folders("matlab")
create_build_folders("python")

# generate site folder with all contents using hte above build folders

def make_full_site():

    if os.path.exists('full_site'):
        shutil.rmtree('full_site')
        os.makedirs('full_site')
    else:
        os.makedirs('full_site')
    
    # build individual lang-ver folder
    to_make = [folder for folder in glob.glob('build1/**') if not os.path.basename(folder).startswith('datajoint')]
    print(to_make)

    # create full version-menu listing using the built folders from above
    f = open('datajoint_theme/version-menu.html', 'w+')
    
    for folder in to_make:
        version = folder.split('/')[1] # 'matlab-v3.2.2'
        f.write('<li class="version-menu"><a href="../../' + version.split("-")[0] + "/" + version.split("-")[1] + '">' + version + '</a></li>\n')
            
    f.close()
       
    # copy over the full version-menu listing to datajoint_theme FIRST, 
    # then build individual folders, and copy to full_site folder 
    for folder in to_make:
        shutil.copy2('datajoint_theme/version-menu.html', folder + "/datajoint_theme/version-menu.html") 
        subprocess.Popen(["make", "site"], cwd=folder).wait()
        version = folder.split('/')[1] # 'matlab-v3.2.2'
        shutil.copytree(folder + "/site", 'full_site/' + version.split("-")[0] + "/" + version.split("-")[1])

        
 

make_full_site()
    
