from os.path import basename
from django.template import RequestContext
from django.shortcuts import render_to_response
from .forms import EndgameSelect
from .r import EndgameChart
# Create your views here.



def index(request):
    return render_to_response('matches_index.html', {},
                              context_instance=RequestContext(request))

def endgame(request):
    if request.method == 'POST':
        select_form = EndgameSelect(request.POST)
        if select_form.is_valid:

            player_list = select_form.data.getlist('players')
            x_var = select_form.data.getlist('x_var')
            y_var = select_form.data.getlist('y_var')
            split_var = select_form.data.getlist('split_var')
            group_var = select_form.data.getlist('group_var')
            image = EndgameChart(player_list,x_var,y_var,split_var,group_var)
            imagebase = basename(image.name)

    else:
        select_form = EndgameSelect()
        image = ''
        imagebase = ''
        player_list = ''
        x_var = ''
        y_var = ''
        split_var = ''
        group_var = ''
    return render_to_response('endgames.html',
                             {'form':select_form,'image':image,
                              'imagebase':imagebase
                             },
                            context_instance=RequestContext(request))

