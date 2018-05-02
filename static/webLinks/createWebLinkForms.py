# -*- coding: utf-8 -*-
"""
Created on Tue May  9 08:42:44 2017

@author: Beau.Uriona
"""
import os

class ChartGroup(object):
    def __init__(self, directoryName, webText):
        self.directoryName = directoryName
        self.webText = webText
class ChartPic(object):
    def __init__(self, directoryName, picUrl):
        self.directoryName = directoryName
        self.picUrl = picUrl
class ChartBlurb(object):
    def __init__(self, directoryName, blurbText):
        self.directoryName = directoryName
        self.blurbText = blurbText       
def writeToWebLinkFile(webStr):
    with open(r'webLinkForms' + pageFor + pageType + '.html', 'w') as webPage:
        webPage.write(webStr)
########### USED TO CREATE TEXT FILES OF THE DROPDOWNS ##########################
#    with open(r'webLinkForms' + pageFor + pageType + '.txt', 'w') as webLinks:
#        txtStr = webStr
#        txtStr = txtStr.replace(r'<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Forms</title></head><body>',r'')
#        txtStr = txtStr.replace(r'</body></html>',r'')
#        webLinks.write(txtStr)

if __name__ == '__main__':
           
    chartGroupNames = [
                  ChartGroup(r'..\..\basinCharts\POR\PREC', r'Period of Record Precipitation'),
                  ChartGroup(r'..\..\basinCharts\POR\SMS', r'Period of Record Soil Moisture'),
                  ChartGroup(r'..\..\basinCharts\POR\STO', r'Period of Record Soil Temperature'),
                  ChartGroup(r'..\..\basinCharts\POR\TAVG', r'Period of Record Avg. Daily Temperature'),
                  ChartGroup(r'..\..\basinCharts\POR\WTEQ', r'Period of Record Snow Water Equivalent'),
                  ChartGroup(r'..\..\basinCharts\Proj\WTEQ', r'Snow Water Equivalent Projections'),
                  ChartGroup(r'..\..\basinCharts\Proj\PREC', r'Precipitation Projections'),
                  ChartGroup(r'..\..\basinMaps', r'Basin Maps'),
                  ChartGroup(r'..\..\siteCharts\POR\PREC', r'Period of Record Precipitation'),
                  ChartGroup(r'..\..\siteCharts\POR\WTEQ', r'Period of Record Snow Water Equivalent'),
                  ChartGroup(r'..\..\siteCharts\POR\TAVG', r'Period of Record Avg. Daily Temperature'),
                  ChartGroup(r'..\..\siteCharts\POR\SMS', r'Period of Record Soil Moisture'),
                  ChartGroup(r'..\..\siteCharts\Proj\WTEQ', r'Snow Water Equivalent Projections'),
                  ChartGroup(r'..\..\siteCharts\Proj\PREC', r'Precipitation Projections'),
                  ChartGroup(r'..\..\siteCharts\Contour\SMS', r'Soil Moisture Heat Map'),
                  ChartGroup(r'..\..\siteCharts\Contour\STO', r'Soil Temperature Heat Map'),
                  ChartGroup(r'..\..\static', r'Production status and link to this page')]
    
    chartGroupDesc = {}
    for g in chartGroupNames:
        chartGroupDesc[g.directoryName] = g.webText
    
    chartPicUrls = [
                  ChartPic(r'..\..\basinCharts\POR\PREC', r'exPORprecBasins.png'),
                  ChartPic(r'..\..\basinCharts\POR\SMS', r'exPORsmsBasins.png'),
                  ChartPic(r'..\..\basinCharts\POR\STO', r'exPORstoBasins.png'),
                  ChartPic(r'..\..\basinCharts\POR\TAVG', r'exPORtavgBasins.png'),
                  ChartPic(r'..\..\basinCharts\POR\WTEQ', r'exPORsweBasins.png'),
                  ChartPic(r'..\..\basinCharts\Proj\WTEQ', r'exProjSweBasins.png'),
                  ChartPic(r'..\..\basinCharts\Proj\PREC', r'exProjPrecBasins.png'),
                  ChartPic(r'..\..\basinMaps', r'exBasinMap.png'),
                  ChartPic(r'..\..\siteCharts\POR\PREC', r'exPORprecSites.png'),
                  ChartPic(r'..\..\siteCharts\POR\TAVG', r'exPORtavgSites.png'),
                  ChartPic(r'..\..\siteCharts\POR\WTEQ', r'exPORsweSites.png'),
                  ChartPic(r'..\..\siteCharts\POR\SMS', r'exPORsmsSites.png'),
                  ChartPic(r'..\..\siteCharts\Proj\WTEQ', r'exProjSweSites.png'),
                  ChartPic(r'..\..\siteCharts\Proj\PREC', r'exProjPrecSites.png'),
                  ChartPic(r'..\..\siteCharts\Contour\SMS', r'exContourSmsSites.png'),
                  ChartPic(r'..\..\siteCharts\Contour\STO', r'exContourStoSites.png'),
                  ChartPic(r'..\..\static', r'notApplicable.png')]
    
    exChrtNames = {}
    for g in chartPicUrls:
        exChrtNames[g.directoryName] = g.picUrl
    
    chartBlurbText = [ChartBlurb(r'..\..\basinCharts\POR\PREC', r'graph comparing the average of current accumulated precipitation (in inches) of all sites within and adjacent to the watershed with all other years from the historical record.  Graphs also include statistical background data, such as the maximum, normal, and minimum water years, as well as shading based on the 10th, 30th, 50th, 70th, and 90th percentiles. The user can select and compare any year(s).'),
                  ChartBlurb(r'..\..\basinCharts\POR\SMS', r'graph comparing the average of current soil moisture (in % saturation) of all sites within and adjacent to the watershed with all other years from the historical record.  Graphs also include statistical background data, such as the maximum, normal, and minimum water years, as well as shading based on the 10th, 30th, 50th, 70th, and 90th percentiles. The user can select and compare any year(s).'),
                  ChartBlurb(r'..\..\basinCharts\POR\STO', r'graph comparing the average of current soil temperature (in &#176;F) of all sites within and adjacent to the watershed with all other years from the historical record.  Graphs also include statistical background data, such as the maximum, normal, and minimum water years, as well as shading based on the 10th, 30th, 50th, 70th, and 90th percentiles. The user can select and compare any year(s).'),
                  ChartBlurb(r'..\..\basinCharts\POR\TAVG', r'graph comparing the average of current average daily temperature (in &#176;F) of all sites within and adjacent to the watershed with all other years from the historical record.  Graphs also include statistical background data, such as the maximum, normal, and minimum water years, as well as shading based on the 10th, 30th, 50th, 70th, and 90th percentiles. The user can select and compare any year(s).'),
                  ChartBlurb(r'..\..\basinCharts\POR\WTEQ', r'graph comparing the average of current snow water equivalent (in inches) of all sites within and adjacent to the watershed with all other years from the historical record.  Graphs also include statistical background data, such as the maximum, normal, and minimum water years, as well as shading based on the 10th, 30th, 50th, 70th, and 90th percentiles. The user can select and compare any year(s).'),
                  ChartBlurb(r'..\..\basinCharts\Proj\WTEQ', r'graph showing the projected snow water equivalent (in inches) of all sites within and adjacent to the selected watershed for the remainder of the water year, for a range of possible outcomes.  Graphs also include all other years from the historical record, plus statistical background data, such as the maximum, normal, and minimum water years, as well as shading based on the 10th, 30th, 50th, 70th, and 90th percentiles. The user can select and compare any year(s).'),
                  ChartBlurb(r'..\..\basinCharts\Proj\PREC', r'graph showing the projected precipitation (in inches) of all sites within and adjacent to the selected watershed for the remainder of the water year, for a range of possible outcomes.  Graphs also include all other years from the historical record, plus statistical background data, such as the maximum, normal, and minimum water years, as well as shading based on the 10th, 30th, 50th, 70th, and 90th percentiles. The user can select and compare any year(s).'),
                  ChartBlurb(r'..\..\basinMaps', r"displays the sites used within a basin's average calculations."),
                  ChartBlurb(r'..\..\siteCharts\POR\PREC', r'graph comparing the current accumulated precipitation (in inches) for an individual SNOTEL site with all other years from the historical record.  Graphs also include statistical background data, such as the maximum, normal, and minimum water years, as well as shading based on the 10th, 30th, 50th, 70th, and 90th percentiles. The user can select and compare any year(s).'),
                  ChartBlurb(r'..\..\siteCharts\POR\WTEQ', r'graph comparing the current snow water equivalent (in inches) for an individual SNOTEL site with all other years from the historical record.  Graphs also include statistical background data, such as the maximum, normal, and minimum water years, as well as shading based on the 10th, 30th, 50th, 70th, and 90th percentiles. The user can select and compare any year(s).'),
                  ChartBlurb(r'..\..\siteCharts\POR\TAVG', r'graph comparing the average of current average daily temperature (in &#176;F) of a site with all other years from the historical record.  Graphs also include statistical background data, such as the maximum, normal, and minimum water years, as well as shading based on the 10th, 30th, 50th, 70th, and 90th percentiles. The user can select and compare any year(s).'),
                  ChartBlurb(r'..\..\siteCharts\POR\SMS', r'graph comparing the average of current soil moisture (in % saturation) of of a site with all other years from the historical record.  Graphs also include statistical background data, such as the maximum, normal, and minimum water years, as well as shading based on the 10th, 30th, 50th, 70th, and 90th percentiles. The user can select and compare any year(s).'),
                  ChartBlurb(r'..\..\siteCharts\Proj\WTEQ', r'graph showing the projected snow water equivalent (in inches) at an individual SNOTEL site for the remainder of the water year, for a range of possible outcomes.  Graphs also include all other years from the historical record, plus statistical background data, such as the maximum, normal, and minimum water years, as well as shading based on the 10th, 30th, 50th, 70th, and 90th percentiles. The user can select and compare any year(s).'),
                  ChartBlurb(r'..\..\siteCharts\Proj\PREC', r'graph showing the projected precipitation (in inches) at an individual SNOTEL site for the remainder of the water year, for a range of possible outcomes.  Graphs also include all other years from the historical record, plus statistical background data, such as the maximum, normal, and minimum water years, as well as shading based on the 10th, 30th, 50th, 70th, and 90th percentiles. The user can select and compare any year(s).'),
                  ChartBlurb(r'..\..\siteCharts\Contour\SMS', r'graph showing the soil moisture (shaded by % saturation) over the depth of the soil profile.  Graphs also include daily incremental precipitation and snow melt (in inches) for the timing of water supplied from the surface.'),
                  ChartBlurb(r'..\..\siteCharts\Contour\STO', r'graph showing the soil temperature, in (&#176;F), over the depth of the soil profile.'),
                  ChartBlurb(r'..\..\static', r'N/A')]
    
    exChrtBlurbs = {}
    for g in chartBlurbText:
        exChrtBlurbs[g.directoryName] = g.blurbText
    
    pageForList = ['UT','NV_CA','AK','AZ','CA','CO','ID','MT','NM','OR','WA','WY']
    pageTypeList = [r'basin', r'site']
           
    webLinkStr = ''        
    rootDir = '..\..'
    htmlHead = r'<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Forms</title></head><body><table style="width: 700px; height: 311px;" border="0" cellspacing="0" cellpadding="0"><tbody>'
    htmlEnd = r'</tbody></table></body></html>'
    itemPrefixStr = r'<option value="http://www.wcc.nrcs.usda.gov/ftpref/states/ut/iCharts_ECM'
    exChrtSuffix = r'" style="width: 350px; height: 311px; float: right;" /></p>'
    
    for pageFor in pageForList:    
        exChrtPre = r'<p><img src="https://www.wcc.nrcs.usda.gov/ftpref/states/ut/iCharts_ECM/exCharts/' + pageFor + r'/'
        for pageType in pageTypeList:
            webLinkStr = r''
            webLinkStrList = []
            for dirName, subdirList, fileList in os.walk(rootDir, topdown=True):
                subdirList.sort(reverse=True)
                fileList.sort()
                if (len(list([f for f in fileList if f.endswith(r'.html')])) > 0 
                    and pageType in dirName 
                    and (dirName.endswith(pageFor) 
                    and not r'static' in dirName)):
                    
                    chartChartGroupStr = r''
                    prefixStr = (r'<tr><td><form onsubmit="window.open(href=this.site.value,' + 
                             r" 'NRCS AWDB iChart', 'resizable=no,status=no,location=no,toolbar=no,menubar=no,fullscreen=no,scrollbars=yes,dependent=no,width=725,left=10,height=622,top=10'); return false;" + '"><strong style="font-size: 12.24px;"><label for="basin">' +
                             chartGroupDesc.get(dirName.replace('\\' + pageFor,''),r'***PLACEHOLDER PLEASE REPLACE***') + 
                             r'</label></strong><br style="font-size: 12.24px;"><select id="site" name="site">')
                    webLinkStr = webLinkStr + prefixStr
                    webDirName = dirName.replace('\\',r'/').replace(r'../..','')
                    for fname in fileList:
                        if fname.endswith('.html'): 
                            itemDescription = fname.replace(r'.html','')
                            itemSuffixStr = r'">' + itemDescription + r'</option>'
                            chartChartGroupStr = (chartChartGroupStr + '\n' + 
                                                  itemPrefixStr + 
                                                  webDirName + 
                                                  '/%s' % fname + 
                                                  itemSuffixStr)
                    jumpStr = r'<a name="' + exChrtNames.get(dirName.replace('\\' + pageFor,''),r'***PLACEHOLDER PLEASE REPLACE***').replace(r'ex',r'').replace(r'Basins',r'').replace(r'Sites',r'').replace(r'.png',r'') + r'"></a>'
                    suffixStr = (r'</select><p style="font-size: 12.24px;"><input type="submit" value="Open Chart"></p></form><p>' + 
                                 exChrtBlurbs.get(dirName.replace('\\' + pageFor,''),r'***PLACEHOLDER PLEASE REPLACE***') + r'<p></td><td>' + 
                                 exChrtPre + 
                                 exChrtNames.get(dirName.replace('\\' + pageFor,''),r'***PLACEHOLDER PLEASE REPLACE***') + 
                                 exChrtSuffix + jumpStr +
                                 r'</td></tr>')
                    webLinkStr = webLinkStr + jumpStr + chartChartGroupStr + suffixStr
                    webLinkStrList.append(webLinkStr)
                    webLinkStr = ''
#                    webLinkStr = webLinkStr + jumpStr + chartChartGroupStr + suffixStr
            if pageType == 'basin': formOrder = [0,3,7,1,2,4,6,5]
            if pageType == 'site': formOrder = [2,5,0,1,3,4,6]
            webLinkStrList = [webLinkStrList[i] for i in formOrder]
            webLinkStr = ''.join(webLinkStrList)
            webLinkStr = htmlHead + webLinkStr + htmlEnd
            
            writeToWebLinkFile(webLinkStr) 
    