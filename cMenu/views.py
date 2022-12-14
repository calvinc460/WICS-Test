from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, resolve
from django.utils.text import slugify
from cMenu.utils import WrapInQuotes
from django import forms
from cMenu import menucommand_handlers
from cMenu.menucommand_handlers import MENUCOMMAND
from cMenu.models import menuCommands, menuItems, menuGroups
# imports below are WICS-specific
from userprofiles.models import WICSuser

# Create your views here.

@login_required
def LoadMenu(req, menuGroup, menuNum):
# DOCUMENT THIS!!!   ADD COMMENTS!!!  EXPLAIN IT!!!
    # next few lines (and their uses) is WICS-specific, not generic cMenu
    _userorg = WICSuser.objects.get(user=req.user).org

    mnItem_qset = menuItems.objects.filter(MenuGroup = menuGroup, MenuID = menuNum).values('OptionNumber','OptionText','Command','Argument')
    mnuName = mnItem_qset.get(OptionNumber=0)['OptionText']

    mnItem_list = ['' for i in range(20)]
    for m in mnItem_qset:
        if m['OptionNumber']==0: continue
        mHTML = "<a href="
        if m['Command'] == MENUCOMMAND.LoadMenu.value:
            mHTML = mHTML + reverse('LoadMenu', kwargs={'menuGroup': menuGroup, 'menuNum':m['Argument']})
        else:
            cmArg = slugify(m['Argument'])
            if not cmArg: cmArg = 'no-arg-no'
            mHTML = mHTML + reverse('HandleCommand', kwargs={'CommandNum':m['Command'], 'CommandArg': cmArg})
            if m['Command'] != MENUCOMMAND.ExitApplication.value:
                mHTML = mHTML + " target=" + WrapInQuotes("_blank")
        # endif
        mHTML = mHTML + " class=" + WrapInQuotes("btn btn-lg bd-btn-lg btn-outline-secondary mx-auto") + ">" + m['OptionText'] + "</a>"
        mnItem_list[m['OptionNumber']-1] = mHTML

    fullMenuHTML = ""

    for i in range(10):
        fullMenuHTML += ("<div class=" + WrapInQuotes("row") + "><div class=" + WrapInQuotes("col m-1") + ">" + mnItem_list[i] + "</div>")
        fullMenuHTML += ("<div class=" + WrapInQuotes("col m-1") + ">" + mnItem_list[i+10] + "</div></div>")
    ctxt = {'menuName':mnuName , 'menuContents':fullMenuHTML, 'orgname':_userorg.orgname, 'uname':req.user.get_full_name()}
    return render(req, "cMenu.html", context=ctxt)


@login_required
def EditMenu(req, menuGroup, menuNum):
# DOCUMENT THIS!!!   ADD COMMENTS!!!  EXPLAIN IT!!!
    # next few lines (and their uses) is WICS-specific, not generic cMenu
    _userorg = WICSuser.objects.get(user=req.user).org

    # things go bonkers if these are strings
    menuGroup = int(menuGroup)
    menuNum = int(menuNum)

    commandchoices = menuCommands.objects.all()
    def commandchoiceHTML(passedcommand):
        commandchoices_html = ""
        for ch in commandchoices:
            commandchoices_html += "<option value=" + str(ch.Command)
            if ch.Command == passedcommand: commandchoices_html += " selected"
            commandchoices_html += ">" + ch.CommandText + "</option>"
        return commandchoices_html

    mnItem_qset = menuItems.objects.filter(MenuGroup = menuGroup, MenuID = menuNum)     #.values('OptionNumber','OptionText','Command','Argument')
    mnuName = mnItem_qset.get(OptionNumber=0).OptionText

    mnItem_list = [{'OptionText':'',
                    'Command':'',
                    'Argument':''}  
            for i in range(20)]
    changed_data = ''

    if req.method == 'POST':
        # construict mnItem_list from POST data
        for pdat in req.POST.items():
            if "csrf" in pdat[0]: continue
            pdat_line = pdat[0].split('-')
            idx = int(pdat_line[1])-1
            mnItem_list[idx][pdat_line[0]] = pdat[1]
        # compare to mnItem_qset
        # where different, update or add
        # set signal to pass back to form
        for i_0based in range(20):
            i = i_0based + 1
            thisItem = mnItem_list[i_0based]
            thisItem['Command'] = int(thisItem['Command'])
            try:
                mnRec = mnItem_qset.get(OptionNumber=i)
            except:
                mnRec = None

            if thisItem.get('Remove',False):    # later, use makebool since values may be 'on' or 'off'
                if mnRec:
                    mnRec.delete()
                mnItem_list[i_0based] = {'OptionText':'',
                                'Command':'',
                                'Argument':''}
                if changed_data: changed_data += ", "
                changed_data += " Option " + str(i) + " removed"
            else:
                if mnRec:
                    if mnRec.OptionText != thisItem['OptionText'] \
                    or mnRec.Command_id != thisItem['Command'] \
                    or mnRec.Argument != thisItem['Argument']:
                        # mnRec exists, and mnItem_list is changed
                        mnRec.OptionText = thisItem['OptionText']
                        mnRec.Command_id = thisItem['Command'] 
                        mnRec.Argument = thisItem['Argument']
                        mnRec.save()
                        if changed_data: changed_data += ", "
                        changed_data += " Option " + str(i) + " changed"
                else:
                    if thisItem['OptionText'] \
                    or thisItem['Command'] \
                    or thisItem['Argument']:
                        # mnRec does not exist, but mnItem_list is new (has values)
                        mnRec = menuItems(MenuGroup_id = menuGroup,
                            MenuID = menuNum,
                            OptionNumber = i,
                            OptionText = thisItem['OptionText'],
                            Command_id = thisItem['Command'],
                            Argument = thisItem['Argument']
                            )
                        mnRec.save()
                        if changed_data: changed_data += ", "
                        changed_data += " Option " + str(i) + " added"
                #endif mnRec 
        #raise Exception('look at POST data')

    else:
        for m in mnItem_qset:
            mnItem_list[m.OptionNumber-1]['OptionText'] = m.OptionText
            mnItem_list[m.OptionNumber-1]['Command'] = m.Command_id
            mnItem_list[m.OptionNumber-1]['Argument'] = m.Argument
    # endif request.method = 'POST'

    fullMenuHTML = ""
    for i_0based in range(10):
        i = i_0based + 1
        istr = str(i)
        i2 = i+10
        i2str = str(i2)
        fullMenuHTML += "<div class='row'>"
        fullMenuHTML += "<div class='col m-1'> " + istr + " "
        fullMenuHTML += "<input type='text' size='20' name='OptionText-" + istr + "'"
        if mnItem_list[i_0based]['OptionText']: fullMenuHTML += " value = '" + mnItem_list[i_0based]['OptionText'] + "'"
        fullMenuHTML += "></input></div>"
        fullMenuHTML += "<div class='col m-1'> " + i2str + " "
        fullMenuHTML += "<input type='text' size='20' name='OptionText-" + i2str + "'"
        if mnItem_list[i_0based+10]['OptionText']: fullMenuHTML += " value = '" + mnItem_list[i_0based+10]['OptionText'] + "'"
        fullMenuHTML += "></input></div>"
        fullMenuHTML += "</div>"
        
        fullMenuHTML += "<div class='row'>"
        fullMenuHTML += "<div class='col m-1'> Command: "
        fullMenuHTML += "<select style='width:15em' name='Command-" + istr + "'>"
        fullMenuHTML += commandchoiceHTML(mnItem_list[i_0based]['Command'])
        fullMenuHTML += "</select>"
        fullMenuHTML += " Remove:<input type='checkbox' name='Remove-" + istr + "'></input>"
        fullMenuHTML += "</div>"
        fullMenuHTML += "<div class='col m-1'> Command: "
        fullMenuHTML += "<select style='width:15em' name='Command-" + i2str + "'>"
        fullMenuHTML += commandchoiceHTML(mnItem_list[i_0based+10]['Command'])
        fullMenuHTML += "</select>"
        fullMenuHTML += " Remove:<input type='checkbox' name='Remove-" + i2str + "'></input>"
        fullMenuHTML += "</div>"
        fullMenuHTML += "</div>"

        fullMenuHTML += "<div class='row'>"
        fullMenuHTML += "<div class='col m-1'> Argument: "
        fullMenuHTML += "<input type='text' size='20' name='Argument-" + istr + "'"
        if mnItem_list[i_0based]['Argument']: fullMenuHTML += " value = '" + mnItem_list[i_0based]['Argument'] + "'"
        fullMenuHTML += "></input></div>"
        fullMenuHTML += "<div class='col m-1'> Argument: "
        fullMenuHTML += "<input type='text' size='20' name='Argument-" + i2str + "'"
        if mnItem_list[i_0based+10]['Argument']: fullMenuHTML += " value = '" + mnItem_list[i_0based+10]['Argument'] + "'"
        fullMenuHTML += "></input></div>"
        fullMenuHTML += "</div>"

        if i<10:
            fullMenuHTML += "<hr>"
            pass
        
    mnuGoto = {'menuGroup':menuGroup,
                'menuGroup_choices': menuGroups.objects.all(),      # later, when menuGroup<->org built, restrict this
                'menuID':menuNum,
                'menuID_choices':menuItems.objects.filter(MenuGroup=menuGroup,OptionNumber=0)
                }

    ctxt = {'menuName':mnuName , 
            'menuGoto':mnuGoto,
            'menuContents':fullMenuHTML, 
            'changed_data': changed_data,
            'orgname':_userorg.orgname, 
            'uname':req.user.get_full_name()}
    tmplt = "cMenuEdit.html"
    return render(req, tmplt, context=ctxt)


def HandleMenuCommand(req,CommandNum,CommandArg):
    retHTTP = "Command " + menuCommands.objects.get(Command=CommandNum).__str__() + " will be performed with Argument " + CommandArg

    if CommandNum == MENUCOMMAND.LoadMenu.value :
        retHTTP = LoadMenu(req,int(CommandArg))
    elif CommandNum == MENUCOMMAND.FormBrowse.value :
        retHTTP = menucommand_handlers.FormBrowse(req, CommandArg)
    elif CommandNum == MENUCOMMAND.FormAdd.value :
        pass
    elif CommandNum == MENUCOMMAND.ReportView.value :
        pass
    elif CommandNum == MENUCOMMAND.ReportPrint.value :
        pass
    elif CommandNum == MENUCOMMAND.OpenTable.value :
        retHTTP = menucommand_handlers.ShowTable(req, CommandArg)
    elif CommandNum == MENUCOMMAND.OpenQuery.value :
        pass
    elif CommandNum == MENUCOMMAND.RunCode.value :
        fn = getattr(menucommand_handlers, CommandArg)
        retHTTP = fn(req)
    elif CommandNum == MENUCOMMAND.RunSQLStatement.value:
        pass
    elif CommandNum == MENUCOMMAND.ConstructSQLStatement.value:
        pass
    elif CommandNum == MENUCOMMAND.ChangePW.value:
        return HttpResponseRedirect(reverse('change_password'))
    elif CommandNum == MENUCOMMAND.EditMenu.value :
        return HttpResponseRedirect(reverse('EditMenu_init'))
    elif CommandNum == MENUCOMMAND.EditParameters.value :
        pass
    elif CommandNum == MENUCOMMAND.EditGreetings.value :
        pass
    elif CommandNum == MENUCOMMAND.EditPasswords.value :
        pass
    elif CommandNum == MENUCOMMAND.ExitApplication.value :
        return HttpResponseRedirect(reverse('WICSlogout'))
    else:
        pass

    return HttpResponse(retHTTP)