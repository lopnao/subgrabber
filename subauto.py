import logging
import zipfile
import re
import bs4
import os
import requests
import shutil


logging.basicConfig(level=logging.INFO, format=' %(asctime)s -%(levelname)s - %(message)s')


def rargrabber(serieTitre, serieSaison, serieEpisode):
    """ Cherche l'archive de sous-titres sur sous-titres.eu
        Retourne l'achive et la liste des fichiers présents dans l'achive"""
    serie_titre_formatted = serieTitre.lower().replace(' ', '+')
    serieSaison = serieSaison[1]
    # display text while downloading the search page
    logging.debug("Searching for %s .." % serieTitre)
    res = requests.get('https://www.sous-titres.eu/search.html?q=' + serie_titre_formatted)
    res.raise_for_status()

    soup = bs4.BeautifulSoup(res.text, "lxml")
    # Selectionne l'element qui reference vers la pages de la serie
    linkElems = soup.select('li.serie > .icone')
    try:
        for i in range(1):
            serie_page = 'http://www.sous-titres.eu/' + \
                         linkElems[i].get('href') + '#' + 'saison-' + serieSaison
    except IndexError:
        return False
    logging.debug("Searching for Saison %s Episode %s .." % (serieSaison, serieEpisode))  # display
    res = requests.get(serie_page)
    res.raise_for_status()
    l = episodeOrseason(res, serieSaison, serieEpisode)
    return l


def episodeOrseason(res, serieSaison, serieEpisode):
    # Retrieve top search result links.
    soup = bs4.BeautifulSoup(res.text, "lxml")
    href_formatted = "a[href*=" + serieSaison + "x" + serieEpisode + "]"
    href_formattedsaison = "a[href*=S" + serieSaison + "]"
    href_formattedsaison0 = "a[href*=S0" + serieSaison + "]"
    logging.debug('Recherche du fichier sous-titres sur le site...')
    try:
        linkElems = soup.select(href_formatted)
        for i in range(1):
            # webbrowser.open('http://www.sous-titres.eu/series/' + linkElems[i].get('href'))
            res = requests.get('http://www.sous-titres.eu/series/' + linkElems[i].get('href'))
            res.raise_for_status()
            zipTempFile = open('zipTemp.zip', 'wb')
            for chunk in res.iter_content(100000):
                zipTempFile.write(chunk)
            zipTempFile.close()
            logging.debug("Fichier ZIP cree")
            zipTempFile2 = zipfile.ZipFile('zipTemp.zip')
            liste_fichier = zipTempFile2.namelist()
            retour = (zipTempFile2, liste_fichier)
            return retour
    except IndexError:
        try:
            linkElems = soup.select(href_formattedsaison)
            for i in range(1):
                # webbrowser.open('http://www.sous-titres.eu/series/' + linkElems[i].get('href'))
                res = requests.get('http://www.sous-titres.eu/series/' + linkElems[i].get('href'))
                res.raise_for_status()
                zipTempFile = open('zipTemp.zip', 'wb')
                for chunk in res.iter_content(100000):
                    zipTempFile.write(chunk)
                zipTempFile.close()
                logging.debug("Fichier ZIP cree")
                zipTempFile2 = zipfile.ZipFile('zipTemp.zip')
                liste_fichier = zipTempFile2.namelist()
                retour = (zipTempFile2, liste_fichier)
                return retour
        except IndexError:
            try:
                linkElems = soup.select(href_formattedsaison0)
                for i in range(1):
                    # webbrowser.open('http://www.sous-titres.eu/series/' + linkElems[i].get('href'))
                    res = requests.get('http://www.sous-titres.eu/series/' + linkElems[i].get('href'))
                    res.raise_for_status()
                    zipTempFile = open('zipTemp.zip', 'wb')
                    for chunk in res.iter_content(100000):
                        zipTempFile.write(chunk)
                    zipTempFile.close()
                    logging.debug("Fichier ZIP cree")
                    zipTempFile2 = zipfile.ZipFile('zipTemp.zip')
                    liste_fichier = zipTempFile2.namelist()
                    retour = (zipTempFile2, liste_fichier)
                    return retour
            except:
                return False


def subfilechoice(liste_rarfiles_arg, serieSaison, serieEpisode, serieSource, serieTeam):
    if serieSource == 'WEBDL' or serieSource == 'WEB-DL':
        serieSource = '(WEBDL|WEB-DL)'
    if len(serieSaison) == 2 and serieSaison[0] == '0':
        serieSaison = serieSaison + '|' + serieSaison[1]
    if len(serieSaison) == 1:
        serieSaison = serieSaison + '|0' + serieSaison
    choix_st_Pattern1 = re.compile(
        r'^((.*)({0})(.*)({1})(.*)(720p|1080p)?(480p|540p)?(.*)({2})(.*)\.ass)'.format(serieSaison, serieEpisode,
                                                                                       serieTeam),
        re.VERBOSE | re.IGNORECASE)
    choix_st_Pattern2 = re.compile(
        r'^((.*)({0})(.*)({1})(.*)(720p|1080p)?(480p|540p)?(.*)({2})(.*)\.ass)'.format(serieSaison, serieEpisode,
                                                                                       serieSource),
        re.VERBOSE | re.IGNORECASE)
    choix_st_Pattern3 = re.compile(
        r'^((.*)({0})(.*)({1})(.*)(720p|1080p)?(480p|540p)?(.*)({2})(.*)\.srt)'.format(serieSaison, serieEpisode,
                                                                                       serieTeam),
        re.VERBOSE | re.IGNORECASE)
    choix_st_Pattern4 = re.compile(
        r'^((.*)({0})(.*)({1})(.*)(720p|1080p)?(480p|540p)?(.*)({2})(.*)\.srt)'.format(serieSaison, serieEpisode,
                                                                                       serieSource),
        re.VERBOSE | re.IGNORECASE)
    liste_choix = []
    for stfile_potential in liste_rarfiles_arg:
        mo = choix_st_Pattern1.search(stfile_potential)
        mo2 = choix_st_Pattern2.search(stfile_potential)
        mo3 = choix_st_Pattern3.search(stfile_potential)
        mo4 = choix_st_Pattern4.search(stfile_potential)
        if not mo and not mo2 and not mo3 and not mo4:
            continue
        elif mo:
            bon_fichier1 = mo.group(0)
            liste_choix.insert(0, bon_fichier1)
        elif mo2:
            bon_fichier2 = mo2.group(0)
            liste_choix.append(bon_fichier2)
        elif mo3:
            bon_fichier3 = mo3.group(0)
            liste_choix.append(bon_fichier3)
        elif mo4:
            bon_fichier4 = mo4.group(0)
            liste_choix.append(bon_fichier4)
    if liste_choix != []:
        logging.debug("Fichier sous titres trouve .. " + liste_choix[0])
        bon_fichier = liste_choix[0]
        return bon_fichier
    else:
        logging.debug("Pas de bon fichier trouvé")
        return None


def subfilechoice2(liste_rarfiles_arg, serieSaison, serieEpisode, serieSource, serieTeam):
    bon_fichier = None
    if serieSource == 'WEBDL' or serieSource == 'WEB-DL':
        serieSource = 'WEBDL|WEB-DL'
    if len(serieSaison) == 2 and serieSaison[0] == '0':
        serieSaison = serieSaison + '|' + serieSaison[1]
    if len(serieSaison) == 1:
        serieSaison = serieSaison + '|0' + serieSaison
    pattern_stade1 = re.compile(
        r'^((.*)({0})(.*)({1})(.*)\.(ass|srt))'.format(serieSaison, serieEpisode),
        re.VERBOSE | re.IGNORECASE)
    stade1 = []
    for stfile_potential in liste_rarfiles_arg:
        mo = pattern_stade1.search(stfile_potential)
        if mo:
            stade1.append(mo.group(0))
        else:
            continue
    stade2 = []
    pattern_stade2 = re.compile(
        r'^((.*)({0})(.*))'.format(serieTeam),
        re.VERBOSE | re.IGNORECASE)
    for stfile_potential in stade1:
        mo = pattern_stade2.search(stfile_potential)
        if mo:
            stade2.append(mo.group(0))
        else:
            continue
    if stade2 != []:
        bon_fichier = stade2[0]
    else:
        stade2 = stade1
    if bon_fichier:
        return bon_fichier
    stade3 = []
    pattern_stade3 = re.compile(
        r'^((.*)({0})(.*))'.format(serieSource),
        re.VERBOSE | re.IGNORECASE)
    for stfile_potential in stade2:
        mo = pattern_stade3.search(stfile_potential)
        if mo:
            stade3.append(mo.group(0))
        else:
            continue
    if stade3 != []:
        stade4 = stade3
    else:
        stade4 = stade2
    stade5 = []
    pattern_stade5 = re.compile(
        r'^((.*)(720p|1080p)(.*))',
        re.VERBOSE | re.IGNORECASE)
    for stfile_potential in stade4:
        mo = pattern_stade5.search(stfile_potential)
        if mo:
            stade5.append(mo.group(0))
        else:
            continue
    if stade5 != []:
        bon_fichier = stade5[0]
        return bon_fichier
    else:
        stade5 = stade4
    stade6 = []
    pattern_stade6 = re.compile(
        r'^((.*)(480p|540p)(.*))',
        re.VERBOSE | re.IGNORECASE)
    for stfile_potential in stade5:
        mo = pattern_stade6.search(stfile_potential)
        if not mo:
            stade6.append(stfile_potential)
        else:
            continue
    if stade6 != []:
        bon_fichier = stade6[0]
        return bon_fichier
    else:
        return None


def unrarsubfile(zipFile, bon_fichier, fullpathEpisode, fullpathEpisodeFolder):
    bon_fichier_ext = bon_fichier[len(bon_fichier) - 3:len(bon_fichier)]
    zipFile.extract(bon_fichier, fullpathEpisodeFolder)
    fullpathsubfileTemp = os.path.join(fullpathEpisodeFolder, bon_fichier)
    shutil.move(fullpathsubfileTemp, fullpathEpisode + '.fr.' + bon_fichier_ext)
    return True


def subgrabber(serieTitre, serieSaison, serieEpisode, serieSource, serieTeam, fullpathEpisode, fullpathEpisodeFolder):
    rar = rargrabber(serieTitre, serieSaison, serieEpisode)
    if not rar:
        return False
    liste_rarfiles = rar[1]
    bon_fichier = subfilechoice2(liste_rarfiles, serieSaison, serieEpisode, serieSource, serieTeam)
    if not bon_fichier:
        return False
    zipFile = rar[0]
    unrar = unrarsubfile(zipFile, bon_fichier, fullpathEpisode, fullpathEpisodeFolder)
    if unrar:
        return True


workingfolder = "L:\\Grabbed\\alt.binaries.teevee"
# Create RegEx
folderPattern2 = re.compile(r"""^((.*) \s-\s
    (\d\d)                                      #Saison
    \sx\s
    (\d\d)
    (-\d\d)?                                      #Episode
    \s-\s
    (.*)$                                       #TitreEp
    ) #Titre de la serie

    """, re.VERBOSE)

extPattern = re.compile(r"""^(.*\.(..?.?))
    """, re.VERBOSE)


# Loop over the files in the working directory.
def workdir(workingfolder):
    for episodeFolder in os.listdir(workingfolder):
        if os.path.isdir(os.path.join(workingfolder, episodeFolder)):
            mo = folderPattern2.search(episodeFolder)
            if not mo:  # Skip si mauvais formatting
                logging.debug('Mauvais Formatting' + ' ' + episodeFolder)
                continue
            else:
                titrePart = mo.group(2)  # Get the different parts of the foldername.
                saisonPart = mo.group(3)
                if mo.group(5):
                    episodePart = mo.group(4) + mo.group(5)
                else:
                    episodePart = mo.group(4)
                titreEpPart = mo.group(6)

                episodeFolderName = titrePart + ' - ' + 'Saison ' + saisonPart + ' - ' \
                                    + 'Episode ' + episodePart + ' - ' + titreEpPart
                absworkingfolder = os.path.abspath(workingfolder)  # Get the full, absolute file paths.

                # Rename the files.
                logging.debug('Found "%s" ...' % (episodeFolderName))
                achercher = 1
                for subfile in os.listdir(os.path.join(workingfolder, episodeFolder)):

                    mo2 = extPattern.search(subfile)
                    if not mo:
                        continue
                    extType = mo2.group(2)
                    subfilename = mo2.group(1)
                    if extType == 'ass':
                        logging.debug('Fichier sous-titres ass trouve ... %s' % (subfilename))
                        achercher = 0
                    elif extType == 'srt':
                        logging.debug('Fichier sous-titres srt trouve ... %s' % (subfilename))
                        achercher = 0
                    elif extType == 'mkv' and achercher == 1:
                        logging.debug('Fichier sous-titres non trouve  pour %s' % (subfile))
                        videoPattern = re.compile(
                            r'(.*).s(\d\d)e(\d\d).(.*).(HDTV|WEBDL|DVDRIP|WEBRIP|WEB-DL)(.*)-(.*)-(.*).mkv',
                            re.IGNORECASE)
                        mo_video = videoPattern.search(subfile)
                        if not mo_video:
                            logging.debug('Probleme pour reconnaitre Quality et Group')
                            continue
                        qualityPart = mo_video.group(5)
                        groupPart = mo_video.group(8)
                        fullpathEpisodeFolder = os.path.join(workingfolder, episodeFolder)
                        fullpathEpisode = os.path.join(workingfolder, episodeFolder, subfile)
                        fullpathEpisode = fullpathEpisode[:len(fullpathEpisode) - 4]
                        # print('Quality = ' + qualityPart)
                        subgrabberObj = subgrabber(titrePart, saisonPart, episodePart, qualityPart, groupPart,
                                                   fullpathEpisode,
                                                   fullpathEpisodeFolder)
                        if subgrabberObj:
                            logging.info('Sous-Titres telecharges pour ' + subfile)
                        else:
                            logging.error('[ERREUR] Sous-Titres non téléchargés pour ' + subfile)

                        achercher = 1


# TODO : Faire une fonction workdir pour walk les dossiers et lancer un subgrabber()
workdir(workingfolder)
dirs = [entry.path for entry in os.scandir(workingfolder) if entry.is_dir()]
for folder in dirs:
    subdir = [entry.path for entry in os.scandir(folder) if entry.is_dir()]
    workdir(folder)
    for folder2 in subdir:
        workdir(folder2)


# p = subgrabber('Alias', '01', '02', 'WEBRIP', 'KINGS', 'a', 'a')
# print('P = ' + p)
