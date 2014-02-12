from uuid import uuid4
from django.core.files.storage import default_storage
from django.core.files import File
from rpy2.robjects.packages import importr
from rpy2 import robjects
from os.path import splitext

def s3File(myfile, chosen_name=None):
    myfile2 = open(myfile.name, 'r')
    if chosen_name is not None:
        filename = chosen_name+'.png'
    else:
        extension = splitext(myfile.name)[1]
        filename = '1d_{filename}{ext}' .format(filename=str(uuid4()),ext=extension)
    #Try making a new file and sending that to s3
    s3file = default_storage.open(filename, 'w')
    s3file.write(myfile2.read())
    s3file.close()
    myfile2.close()
    print myfile2, myfile
    return s3file


def enforceTheme(robjects):
    cmd = """
    source('datadrivendota/datadrivendota/theme.r')
    trellis.par.set(theme=ddd.theme)"""
    robjects.r(cmd)
    return True

def FailFace():

    grdevices = importr('grDevices')
    imagefile = File(open('failface.png', 'w'))
    grdevices.png(file=imagefile.name, type='cairo',width=850,height=500)
    cmd = """
    x = 2
    a = 1
    b = 2
    x= seq(-10,10,.1)
    y = c(-sqrt(b**2*(1-(x/a)**2)),sqrt(b**2*(1-(x/a)**2)))

    plot(y~rep(x,2),ylim=c(-10,5),xlim=c(-2,6), axis=F, xaxt='n',
        ann=FALSE, yaxt='n', main='No Data Found!')
    points(y~rep(x+4,2),ylim=c(-1.5,1.5))

    xoffset=2
    yoffset=6
    r = 2
    x = seq(-10,10,.1)
    y = sqrt(r**2-(x-xoffset)**2)-yoffset
    points(y~x)

    xoffset=2
    yoffset=10
    r = 4
    x = seq(-0,4,.1)
    y = sqrt(r**2-(x-xoffset)**2)-yoffset
    points(y~x)

    """

    robjects.r(cmd)
    #relation='free' in scales for independent axes
    grdevices.dev_off()
    imagefile.close()

    hosted_file = s3File(imagefile, 'failface')
    return hosted_file

    robjects.r(cmd)
