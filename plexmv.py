
import shutil
from plexapi.server import PlexServer
import configparser
import argparse
import os


class configData():
    interval = 3
    plexServer = ''
    plexToken = ''
    embyServer = ''
    embyUser = ''
    embyPass = ''
    qbServer = ''
    tmdb_api_key = ''
    qbPort = ''
    qbUser = ''
    qbPass = ''
    addPause = False
    dryrun = False


CONFIG = configData()


def readConfig():
    config = configparser.ConfigParser()
    config.read('config.ini')

    # CONFIG.interval = config['PLEX'].getint('interval', 3)
    # 'http://{}:{}'.format(ip, port)
    if 'PLEX' in config:
        CONFIG.plexServer = config['PLEX'].get('server_url', '')
        # https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/
        CONFIG.plexToken = config['PLEX'].get('server_token', '')

    if 'EMBY' in config:
        CONFIG.embyServer = config['EMBY'].get('server_url', '')
        CONFIG.embyUser = config['EMBY'].get('user', '')
        CONFIG.embyPass = config['EMBY'].get('pass', '')

    if 'TMDB' in config:
        CONFIG.tmdb_api_key = config['TMDB'].get('api_key', '')



def loadArgs():
    global ARGS
    parser = argparse.ArgumentParser(
        description='Move location of Plex media items by genres'
    )
    parser.add_argument('--section', help='section of Plex library')
    parser.add_argument('--genre', help='genre to be select')
    parser.add_argument('--todir', help='dir to ../')
    parser.add_argument('--trim-space', help='dir to folder')
    parser.add_argument('--ls-section', help='Section name')
    parser.add_argument('--dryrun',
                        action='store_true',
                        help='print message instead of real move.')
    ARGS = parser.parse_args()


def ensureDir(file_path):
    if os.path.isfile(file_path):
        file_path = os.path.dirname(file_path)
    if not os.path.exists(file_path):
        os.makedirs(file_path)


def pathMove(fromLoc, toLocBase):
    if os.path.islink(fromLoc):
        print('\033[31mSKIP symbolic link: [%s]\033[0m ' % fromLoc)
        return
    if not os.path.exists(fromLoc):
        print('\033[34mNot found, maybe already moved: [%s]\033[0m ' % fromLoc)
        return

    if os.path.isfile(fromLoc):
        print('\033[31mFile: [%s]\033[0m ' % fromLoc)
        fromLoc = os.path.dirname(fromLoc)
    else:
        print('\033[32mDirectory: [%s]\033[0m ' % fromLoc)
    basename = os.path.basename(fromLoc)
    catFolder = os.path.dirname(os.path.dirname(fromLoc))
    if os.path.exists(catFolder):
        destParentDir = os.path.join(catFolder, toLocBase)
        destDir = os.path.join(destParentDir, basename)
        if os.path.exists(fromLoc) and not os.path.exists(destDir):
            print('mvdir ', fromLoc, destDir)
            if not ARGS.dryrun:
                ensureDir(destParentDir)
                shutil.move(fromLoc, destDir)


def printLocation(lsSection):
    if not (CONFIG.plexServer and CONFIG.plexToken):
        print("Set the 'server_token' and 'server_url' in config.ini")
        return

    print("Connect to the Plex server: " + CONFIG.plexServer)
    baseurl = CONFIG.plexServer  # 'http://{}:{}'.format(ip, port)
    plex = PlexServer(baseurl, CONFIG.plexToken)
    medias = plex.library.section(lsSection)
    # for idx, video in enumerate(plex.library.all()):
    for idx, video in enumerate(medias.all()):
        print(video.title)
        if len(video.locations) > 0:
            for c, loc in enumerate(video.locations):
                print("  %d >> %s" % (c, loc))
        else:
            print("  >> " + '\033[33mNo location: %s \033[0m' % video.title)


def movePlexLibrary():
    if not (CONFIG.plexServer and CONFIG.plexToken):
        print("Set the 'server_token' and 'server_url' in config.ini")
        return
    if not (ARGS.section):
        print("--section")
        return 

    print("Connect to the Plex server: " + CONFIG.plexServer)
    baseurl = CONFIG.plexServer  # 'http://{}:{}'.format(ip, port)
    plex = PlexServer(baseurl, CONFIG.plexToken)
    medias = plex.library.section(ARGS.section)
    # for idx, video in enumerate(plex.library.all()):
    docuCount = 0
    for idx, video in enumerate(medias.all()):
        # gtags = [g for g in video.genres if g.tag == '纪录']
        hasDocu = next((g for g in video.genres if g.tag == ARGS.genre), None)
        if hasDocu:
            docuCount += 1
            print(str(docuCount) + '  ' + video.title)
                # for g in video.genres:
                #     print(" >>" + g.tag)
            if len(video.locations) > 0:
                for loc in video.locations:
                    # print(loc)
                    pathMove(loc, ARGS.todir)
            else:
                print('\033[33mNo location: %s \033[0m' % video.title)


def trimTrailingSpaceOfFolderName(sectionFolder):
    for idx, fn in enumerate(os.listdir(sectionFolder)):
        if fn.endswith(' '):
            print(f'{idx}: [{fn}]')
            newfn = os.path.join(sectionFolder, fn.strip())
            if not os.path.exists(newfn):
                os.rename(os.path.join(sectionFolder, fn), newfn)
            else:
                print(f"[{newfn}] exists.")
    print(f"Total: {idx}")


def main():
    loadArgs()
    readConfig()
    if ARGS.trim_space:
        trimTrailingSpaceOfFolderName(ARGS.trim_space)
    elif ARGS.ls_section:
        printLocation(ARGS.ls_section)
    else:
        # if ARGS.plex_move:
        movePlexLibrary()

if __name__ == '__main__':
    main()



