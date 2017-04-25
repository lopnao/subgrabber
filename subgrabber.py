#! python3
#SubGrabber est un module python pour scanner
#un ou plusieurs dossiers contenant des episodes de series tv
#il evalue si un fichier de sous titres est present pour chaque fichier
#video
#Si aucun fichier de soustitres n est present
#il rechercher sur le site sous-titres.eu s'il trouve une version adaptee
#et l extraie la copie et la renomme

#Part 1
#Check les soustitres
import shutil, re , os, logging, requests, bs4, webbrowser, zipfile
logging.basicConfig(level=logging.INFO, format=' %(asctime)s -%(levelname)s - %(message)s')
def findserie(serieTitre, serieSaison, serieEpisode, serieSource, serieTeam, fullpathEpisode):
    serie_titre_formatted = serieTitre.lower().replace(' ', '+')

    logging.info("Searching for %s .." % (serieTitre)) # display text while downloading the search page
    res = requests.get('https://www.sous-titres.eu/search.html?q=' + serie_titre_formatted)
    res.raise_for_status()



    # Retrieve top search result links.
    soup = bs4.BeautifulSoup(res.text)
    # Open a browser tab for each result.
    linkElems = soup.select('.icone')

    for i in range(1):
        serie_page = 'http://www.sous-titres.eu/' + linkElems[i].get('href')


    logging.info("Searching for Saison %s Episode %s .." % (serieSaison, serieEpisode)) # display
    res = requests.get(serie_page)
    res.raise_for_status()



    # Retrieve top search result links.
    soup = bs4.BeautifulSoup(res.text)
    href_formatted = "a[href*="+serieSaison+"x"+serieEpisode+"]"
    # Open a browser tab for each result.
    linkElems = soup.select(href_formatted)
    for i in range(1):
        #webbrowser.open('http://www.sous-titres.eu/series/' + linkElems[i].get('href'))
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

            """ % serieTeam, re.VERBOSE|re.IGNORECASE)
        choix_st_Pattern2 = re.compile(r"""^((.*)%s
            (.*)(VF|FR)(.*)\.srt$
            )

            """ % serieTeam, re.VERBOSE|re.IGNORECASE)
        choix_st_Pattern3 = re.compile(r"""^((.*)%s
            (.*)(VF|FR)(.*)\.ass$
            )

            """ % serieSource, re.VERBOSE|re.IGNORECASE)
        choix_st_Pattern4 = re.compile(r"""^((.*)%s
            (.*)(VF|FR)(.*)\.srt$
            )

            """ % serieSource, re.VERBOSE|re.IGNORECASE)
        liste_choix = []
        for fichier in liste_fichier:
            mo = choix_st_Pattern1.search(fichier)
            mo2 = choix_st_Pattern2.search(fichier)
            mo3 = choix_st_Pattern3.search(fichier)
            mo4 = choix_st_Pattern4.search(fichier)
                # Skip si mauvais formatting
            if mo == None and mo2 == None and mo3 == None and mo4 == None:
                continue
            elif mo!=None:
                bon_fichier1 = mo.group(0)
                liste_choix[0] = bon_fichier1
            elif mo2!=None:
                bon_fichier2 = mo2.group(0)
                liste_choix.append(bon_fichier2)
            elif mo3!=None:
                bon_fichier3 = mo3.group(0)
                liste_choix.append(bon_fichier3)
            elif mo4!=None:
                bon_fichier4 = mo4.group(0)
                liste_choix.append(bon_fichier4)
        if liste_choix != []:
            logging.info("Fichier sous titres trouve .. "+liste_choix[0])
            zipTempFile2.extract(liste_choix[0], fullpathEpisode+'.fr.ass')
        else:
            logging.info("Pas de bon fichier trouve")



workingfolder = "L:\\Grabbed\\alt.binaries.teevee\\The TEST"
#Create RegEx
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
for episodeFolder in os.listdir(workingfolder):
    mo = folderPattern2.search(episodeFolder)
        # Skip si mauvais formatting
    if mo == None:
        print('Mauvais Formatting' +' '+ episodeFolder)
        continue

    # Get the different parts of the foldername.
    titrePart = mo.group(2)
    saisonPart = mo.group(3)
    if mo.group(5)!=None:
        episodePart = mo.group(4)+mo.group(5)
    else:
        episodePart = mo.group(4)
    titreEpPart = mo.group(6)

    episodeFolderName = titrePart + ' - ' + 'Saison ' + saisonPart + ' - '\
            +'Episode ' + episodePart + ' - ' + titreEpPart
    # Get the full, absolute file paths.
    absworkingfolder = os.path.abspath(workingfolder)

    # Rename the files.
    logging.info('Found "%s" ...' % (episodeFolderName))
    achercher = 1
    for subfile in os.listdir(os.path.join(workingfolder, episodeFolder)):

        mo2 = extPattern.search(subfile)
        if mo == None:
            continue
        extType = mo2.group(2)
        subfilename = mo2.group(1)
        if extType == 'ass':
            logging.info('Fichier sous-titres trouve ... %s' % (subfilename))
            achercher = 0
        elif extType == 'srt':
            logging.info('Fichier sous-titres trouve ... %s' % (subfilename))
            achercher = 0
        elif extType == 'mkv' and achercher == 1:
            logging.info('Fichier sous-titres non trouve  pour %s' % (subfilename))
            fullpathEpisode = os.path.join(workingfolder, episodeFolder, subfilename)
            fullpathEpisode = fullpathEpisode[:len(fullpathEpisode)-4]

            achercher = 1
