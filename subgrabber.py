#!python3
# SubGrabber est un module python pour scanner
# un ou plusieurs dossiers contenant des episodes de series tv
# il evalue si un fichier de sous titres est present pour chaque fichier
# video
# Si aucun fichier de soustitres n est present
# il rechercher sur le site sous-titres.eu s'il trouve une version adaptee
# et l extraie la copie et la renomme

# Part 1
# Check les soustitres
import shutil
import re
import os
import logging
import requests
import bs4
import webbrowser
import zipfile

logging.basicConfig(level=logging.INFO, format=' %(asctime)s -%(levelname)s - %(message)s')


def findserie(serieTitre, serieSaison, serieEpisode, serieSource, serieTeam,
              fullpathEpisode, fullpathEpisodeFolder):
    serie_titre_formatted = serieTitre.lower().replace(' ', '+')
    serieSaison = serieSaison[1]
    # display text while downloading the search page
    logging.info("Searching for %s .." % serieTitre)
    res = requests.get('https://www.sous-titres.eu/search.html?q=' + serie_titre_formatted)
    res.raise_for_status()

    # Retrieve top search result links.
    soup = bs4.BeautifulSoup(res.text, "lxml")
    # Open a browser tab for each result.
    linkElems = soup.select('.icone')

    for i in range(1):
        serie_page = 'http://www.sous-titres.eu/' + \
                     linkElems[i].get('href') + '#' + 'saison-' + serieSaison
    logging.info("Searching for Saison %s Episode %s .." % (serieSaison, serieEpisode))  # display
    res = requests.get(serie_page)
    res.raise_for_status()

    # Retrieve top search result links.
    soup = bs4.BeautifulSoup(res.text, "lxml")
    href_formatted = "a[href*=" + serieSaison + "x" + serieEpisode + "]"
    href_formattedsaison = "a[href*=S" + serieSaison + "]"
    # Open a browser tab for each result.
    linkElems = soup.select(href_formatted)

    logging.info('Recherche du fichier sous-titres sur le site...')
    for i in range(1):
        # webbrowser.open('http://www.sous-titres.eu/series/' + linkElems[i].get('href'))
        res = requests.get('http://www.sous-titres.eu/series/' + linkElems[i].get('href'))
        res.raise_for_status()
        zipTempFile = open('zipTemp.zip', 'wb')
        for chunk in res.iter_content(100000):
            zipTempFile.write(chunk)
        zipTempFile.close()
        logging.info("Fichier ZIP cree")
        zipTempFile2 = zipfile.ZipFile('zipTemp.zip')
        liste_fichier = zipTempFile2.namelist()
        logging.info("Choix du bon fichier soustitres")
        choix_st_Pattern1 = re.compile(r"""^((.*)%s
            (.*)(VF|FR)(.*)\.ass$
            )

            """ % serieTeam, re.VERBOSE | re.IGNORECASE)
        choix_st_Pattern2 = re.compile(r"""^((.*)%s
            (.*)(VF|FR)(.*)\.srt$
            )

            """ % serieTeam, re.VERBOSE | re.IGNORECASE)
        choix_st_Pattern3 = re.compile(r"""^((.*)%s
            (.*)(VF|FR)(.*)\.ass$
            )

            """ % serieSource, re.VERBOSE | re.IGNORECASE)
        choix_st_Pattern4 = re.compile(r"""^((.*)%s
            (.*)(VF|FR)(.*)\.srt$
            )

            """ % serieSource, re.VERBOSE | re.IGNORECASE)
        choix_st_Pattern5 = re.compile(r"""^((.*)%s
                    (.*)(.*)\.ass$
                    )

                    """ % serieTeam, re.VERBOSE | re.IGNORECASE)
        choix_st_Pattern6 = re.compile(r"""^((.*)%s
                    (.*)(.*)\.srt$
                    )

                    """ % serieTeam, re.VERBOSE | re.IGNORECASE)
        choix_st_Pattern7 = re.compile(r"""^((.*)%s
                    (.*)(.*)\.ass$
                    )

                    """ % serieSource, re.VERBOSE | re.IGNORECASE)
        choix_st_Pattern8 = re.compile(r"""^((.*)(%s)(.*)(.srt))""" % serieSource, re.VERBOSE | re.IGNORECASE)
        liste_choix = []
        for fichier in liste_fichier:
            mo = choix_st_Pattern1.search(fichier)
            mo2 = choix_st_Pattern2.search(fichier)
            mo3 = choix_st_Pattern3.search(fichier)
            mo4 = choix_st_Pattern4.search(fichier)
            mo5 = choix_st_Pattern5.search(fichier)
            mo6 = choix_st_Pattern6.search(fichier)
            mo7 = choix_st_Pattern7.search(fichier)
            mo8 = choix_st_Pattern8.search(fichier)
            # Skip si mauvais formatting
            if mo == None and mo2 == None and mo3 == None and mo4 == None and mo5 == None and mo6 == None and mo7 == None and mo8 == None:
                continue
            elif mo != None:
                bon_fichier1 = mo.group(0)
                liste_choix[0] = bon_fichier1
            elif mo2 != None:
                bon_fichier2 = mo2.group(0)
                liste_choix.append(bon_fichier2)
            elif mo3 != None:
                bon_fichier3 = mo3.group(0)
                liste_choix.append(bon_fichier3)
            elif mo4 != None:
                bon_fichier4 = mo4.group(0)
                liste_choix.append(bon_fichier4)
            elif mo5 != None:
                bon_fichier5 = mo5.group(0)
                liste_choix.append(bon_fichier5)
            elif mo6 != None:
                bon_fichier6 = mo6.group(0)
                liste_choix.append(bon_fichier6)
            elif mo7 != None:
                bon_fichier7 = mo7.group(0)
                liste_choix.append(bon_fichier7)
            elif mo8 != None:
                bon_fichier8 = mo8.group(0)
                liste_choix.append(bon_fichier8)
        if liste_choix != []:
            logging.info("Fichier sous titres trouve .. " + liste_choix[0])
            bon_fichier = liste_choix[0]
            bon_fichier_ext = bon_fichier[len(bon_fichier) - 3:len(bon_fichier)]
            zipTempFile2.extract(bon_fichier, fullpathEpisodeFolder)
            fullpathsubfileTemp = os.path.join(fullpathEpisodeFolder, bon_fichier)
            shutil.move(fullpathsubfileTemp, fullpathEpisode + '.fr.' + bon_fichier_ext)
        else:
            logging.info("Pas de bon fichier trouve")


workingfolder = "L:\\Grabbed\\alt.binaries.teevee\\The TEST"
# Create RegEx
folderPattern = re.compile(r"""^(.*?)   #Titre de la serie
    (\s)                                  #Espace
    (\d\d)                              #Saison
    (\s)                                  #Espace
    (x)                                 #Separateur
    (\s)                                  #Espace
    (\d\d)                              #Espisode
    (\s)                                  #Espace
    (-)                                 #Separateur
    (\s)                                  #Espace
    (.*?)                               #Titre
    """, re.VERBOSE)

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
        mo = folderPattern2.search(episodeFolder)
        # Skip si mauvais formatting
        if not mo:
            logging.info('Mauvais Formatting' + ' ' + episodeFolder)
            continue
        else:
            # Get the different parts of the foldername.
            titrePart = mo.group(2)
            saisonPart = mo.group(3)
            if mo.group(5):
                episodePart = mo.group(4) + mo.group(5)
            else:
                episodePart = mo.group(4)
            titreEpPart = mo.group(6)

            episodeFolderName = titrePart + ' - ' + 'Saison ' + saisonPart + ' - ' \
                                + 'Episode ' + episodePart + ' - ' + titreEpPart
            # Get the full, absolute file paths.
            absworkingfolder = os.path.abspath(workingfolder)

            # Rename the files.
            logging.info('Found "%s" ...' % (episodeFolderName))
            achercher = 1
            for subfile in os.listdir(os.path.join(workingfolder, episodeFolder)):

                mo2 = extPattern.search(subfile)
                if not mo:
                    continue
                extType = mo2.group(2)
                subfilename = mo2.group(1)
                if extType == 'ass':
                    logging.info('Fichier sous-titres ass trouve ... %s' % (subfilename))
                    achercher = 0
                elif extType == 'srt':
                    logging.info('Fichier sous-titres srt trouve ... %s' % (subfilename))
                    achercher = 0
                elif extType == 'mkv' and achercher == 1:
                    logging.info('Fichier sous-titres non trouve  pour %s' % (subfile))
                    videoPattern = re.compile(
                        r'(.*).s(\d\d)e(\d\d).(.*).(HDTV|WEBDL|DVDRIP|WEBRIP|WEB-DL)(.*)-(.*)-(.*).mkv',
                        re.IGNORECASE)
                    mo_video = videoPattern.search(subfile)
                    if not mo_video:
                        logging.info('Probleme pour reconnaitre Quality et Group')
                        continue
                    qualityPart = mo_video.group(5)
                    groupPart = mo_video.group(8)
                    fullpathEpisodeFolder = os.path.join(workingfolder, episodeFolder)
                    fullpathEpisode = os.path.join(workingfolder, episodeFolder, subfile)
                    fullpathEpisode = fullpathEpisode[:len(fullpathEpisode) - 4]
                    # print('Quality = ' + qualityPart)
                    if qualityPart == 'WEBDL' or qualityPart == 'WEB-DL' or qualityPart == 'webdl' or qualityPart == 'web-dl':
                        findserie(titrePart, saisonPart, episodePart, 'WEBDL', groupPart, fullpathEpisode,
                                  fullpathEpisodeFolder)
                        findserie(titrePart, saisonPart, episodePart, 'WEB-DL', groupPart, fullpathEpisode,
                                  fullpathEpisodeFolder)
                    else:
                        findserie(titrePart, saisonPart, episodePart, qualityPart, groupPart, fullpathEpisode,
                                  fullpathEpisodeFolder)
                    # print(titrePart + saisonPart + episodePart + qualityPart + groupPart)
                    logging.info('Sous-Titres telecharges pour %s' % subfile)

                    achercher = 1


for folder in os.listdir(workingfolder):
    workdir(workingfolder)
    # print(folder)
    # for subfolder in os.walk(workingfolder):
    #     print(subfolder)
    # # for subfolder in os.listdir(folder):
    # #     print(subfolder)
    # #     workdir(subfolder)
    # logging.info(folder)