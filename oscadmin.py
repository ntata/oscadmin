import commands
import datetime
import os.path
import sys
import time
import urwid   # python console user interface library


PROGRAM_NAME               = "OpenStack Cluster Admin"
PROGRAM_VERSION            = "0.1"
LBL_VERSION                = "Version"

# required and optional indicators for form fields
REQ                        = "* "
OPT                        = "  "

UI_TEXT_YES                = "Yes"
UI_TEXT_NO                 = "No"
UI_TEXT_OK                 = "OK"

MNU_PLACEHOLDER            = "** placeholder **"


# ***** Main Menu *****
MNU_PROGRAM                = "Program"
MNU_CLUSTER_ADMIN          = "Cluster Admin"
MNU_SERVERS                = "Servers"
MNU_BLOCK_STORAGE          = "Block Storage (cinder)"
MNU_CEPH                   = "Ceph Storage"
MNU_COMPUTE                = "Compute/VM (nova)"
MNU_DASHBOARD              = "Dashboard (horizon)"
MNU_NETWORK                = "Network (neutron)"
MNU_OBJECT_STORAGE         = "Object Storage (swift)"
MNU_IMAGES                 = "OS Images (glance)"
MNU_SECURITY               = "Security (keystone)"
MNU_HELP                   = "Help"


# ***** Program *****
MNU_PROG_ABOUT             = "About"
MNU_PROG_SYS_INFO          = "Sys Info"
MNU_PROG_PYTHON_INFO       = "Python Info"
MNU_PROG_QUIT              = "Quit"

# ***** Cluster Admin *****
MNU_CLSTR_DEFINE           = "Define Cluster"
MNU_CLSTR_OPEN             = "Open Cluster"
MNU_CLSTR_CLOSE            = "Close Cluster"
MNU_CLSTR_HEALTH           = "Health Check"
MNU_CLSTR_PING             = "Ping"
MNU_CLSTR_UPTIME           = "Uptime"
MNU_CLSTR_LOAD_AVG         = "Load Average"
MNU_CLSTR_OS               = "Operating System"
MNU_CLSTR_HW_REPORT        = "Hardware Report"

# ***** Servers *****
MNU_SRV_CPUS               = "CPUs"
MNU_SRV_DISKS              = "Disks"
MNU_SRV_FILESYSTEMS        = "Filesystems"
MNU_SRV_LOGS               = "Logs"
MNU_SRV_MEMORY             = "Memory"
MNU_SRV_NET_INTERFACES     = "Network Interfaces"
MNU_SRV_OS                 = "Operating Systems"
MNU_SRV_PACKAGES           = "Packages"
MNU_SRV_PROCESSES          = "Processes"
MNU_SRV_USERS              = "Users"

# ***** Block Storage *****
MNU_BLK_STOR_HEALTH        = "Health Check"
MNU_BLK_STOR_VOLUMES       = "Volumes"
MNU_BLK_STOR_ATTACHMENTS   = "Attachments"
MNU_BLK_STOR_SNAPSHOTS     = "Snapshots"
MNU_BLK_STOR_IMAGES        = "Images"
MNU_BLK_STOR_PLUGINS       = "Plugins"

# ***** Ceph *****
MNU_CEPH_HEALTH            = "Health Check"
MNU_CEPH_MON               = "Monitors"
MNU_CEPH_OSD               = "OSD"
MNU_CEPH_POOLS             = "Pools"
MNU_CEPH_RGW               = "Rados Gateway"
MNU_CEPH_SECURITY          = "Security"

# ***** Compute *****
MNU_COMPUTE_DB             = "Database"
MNU_COMPUTE_API            = "API"
MNU_COMPUTE_AUTH           = "Authentication"
MNU_COMPUTE_FLAVORS        = "Flavors"
MNU_COMPUTE_IMAGES         = "Images"
MNU_COMPUTE_INSTANCES      = "Instances"

# ***** Network *****
MNU_NET_PLUGINS            = "Plugins"
MNU_NET_AGENTS             = "Agents"
MNU_NET_PROVIDER_NET       = "Provider Networks"
MNU_NET_TENANT_NET         = "Tenant Networks"
MNU_NET_NAMESPACES         = "Namespaces"
MNU_NET_TRAFFIC            = "Traffic"

# ***** Object Storage *****
MNU_OBJ_STOR_HEALTH        = "Health Check"
MNU_OBJ_STOR_DEVICES       = "Devices"
MNU_OBJ_STOR_LOGS          = "Logs"
MNU_OBJ_STOR_PROCESSES     = "Running Processes"
MNU_OBJ_STOR_AUDITOR       = "Auditor"
MNU_OBJ_STOR_MIDDLEWARE    = "Middleware"
MNU_OBJ_STOR_RECON         = "Recon"
MNU_OBJ_STOR_RINGS         = "Rings"
MNU_OBJ_STOR_POLICIES      = "Storage Policies"
MNU_OBJ_STOR_SECURITY      = "Security"
MNU_OBJ_STOR_STATUS        = "Status"
MNU_OBJ_STOR_S3            = "S3"

# ***** Security *****
MNU_SEC_USERS              = "Users"
MNU_SEC_TENANTS            = "Tenants"
MNU_SEC_ROLES              = "Roles"
MNU_SEC_CREDENTIALS        = "Credentials"
MNU_SEC_AUTHENTICATION     = "Authentication"
MNU_SEC_TOKENS             = "Tokens"
MNU_SEC_SERVICES           = "Services"
MNU_SEC_ENDPOINTS          = "Endpoints"



# TT = 'tool tip' (help text for individual fields)

F_CHK = 'checkbox'
F_TXT = 'text'       # text entry/edit field

field_mgr = None


def system_time_millis():
    return int(time.time() * 1000)


def close_box(button):
    top.pop()


def display_output_lines(title, output_lines):
    body = [urwid.Text(title), urwid.Divider()]
    for output_line in output_lines:
        t = urwid.Text(output_line)
        body.append(urwid.AttrMap(t, None, focus_map='reversed'))
    body.append(urwid.Divider())
    btn = urwid.Button('Dismiss')
    urwid.connect_signal(btn, 'click', close_box)
    btn = urwid.AttrMap(btn, None, focus_map='reversed')
    body.append(btn)
    w = urwid.ListBox(urwid.SimpleFocusListWalker(body))
    box = urwid.BoxAdapter(w, height=20)
    top.open_output_box(urwid.Filler(box))


def read_file_lines(file_path):
    with open(file_path) as f:
        return f.readlines()
    return None


class CascadingBoxes(urwid.WidgetPlaceholder):
    max_box_levels = 4

    def __init__(self, box):
        super(CascadingBoxes, self).__init__(urwid.SolidFill(u'/'))
        self.box_level = 0
        self.open_box(box)

    def open_box(self, box):
        self.original_widget = urwid.Overlay(urwid.LineBox(box),
            self.original_widget,
            align='center', width=('relative', 80),
            valign='middle', height=('relative', 80),
            min_width=24, min_height=8,
            left=self.box_level * 3,
            right=(self.max_box_levels - self.box_level - 1) * 3,
            top=self.box_level * 2,
            bottom=(self.max_box_levels - self.box_level - 1) * 2)
        self.box_level += 1

    def open_output_box(self, box):
        self.original_widget = urwid.Overlay(urwid.LineBox(box),
            self.original_widget,
            align='center', width=('relative', 80),
            valign='middle', height=('relative', 80),
            min_width=75, min_height=20,
            left=10,
            right=10,
            top=2,
            bottom=3)
        self.box_level += 1

    def pop(self):
        self.original_widget = self.original_widget[0]
        self.box_level -= 1

    def keypress(self, size, key):
        if key == 'esc' and self.box_level > 1:
            self.pop()
        else:
            return super(CascadingBoxes, self).keypress(size, key)


class FieldManager(object):
    """
    This class manages the field data without being entangled in the
    implementation details of the widget set.
    """
    def __init__(self):
        self.getters = {}
        self.required_checkers = {}
        self.label_getters = {}

    def set_required_checker(self, name, function):
        self.required_checkers[name] = function

    def set_label_getter(self, name, function):
        self.label_getters[name] = function

    def set_getter(self, name, function):
        """
        This is where we collect all of the field getter functions.
        """
        self.getters[name] = function

    def get_value(self, name):
        """
        This will actually get the value associated with a field name.
        """
        return self.getters[name]()

    def get_value_dict(self):
        """
        Dump everything we've got.
        """
        missing_values = []
        retval = {}
        for key in self.getters:
            fld_required = self.required_checkers[key]()
            fld_value = self.getters[key]()
            if fld_required:
                if 0 == len(fld_value):
                    lbl = self.label_getters[key]()
                    missing_values.append(lbl)

            retval[key] = fld_value
        if len(missing_values) > 0:
            display_output_lines('Missing Required Fields', missing_values)
            return None
        else:
            return retval


def get_field(field_def, fieldmgr):
    fld_label     = field_def[0]
    fld_name      = field_def[1]
    fld_type      = field_def[2]
    fld_tooltip   = field_def[3]
    fld_max_chars = field_def[4]
    fld_validator = field_def[5]

    # we don't have hanging indent, but we can stick a bullet out into the
    # left column.
    label = urwid.Text(('label', fld_label))
    colon = urwid.Text(('label', ': '))

    if fld_type == F_TXT:
        field_widget = urwid.Edit('', '')
        def get_label():
            return fld_label
        def is_required():
            # if it starts with our required prefix
            pos_req = fld_label.find(REQ)
            return pos_req == 0
        def getter():
            """
            Closure around urwid.Edit.get_edit_text(), which we'll
            use to scrape the value out when we're all done.
            """
            return field_widget.get_edit_text()
        fieldmgr.set_getter(fld_name, getter)
        fieldmgr.set_required_checker(fld_name, is_required)
        fieldmgr.set_label_getter(fld_name, get_label)
    elif fld_type == F_CHK:
        field_widget = urwid.CheckBox('')
        def get_label():
            return fld_label
        def is_required():
            return False

        def getter():
            """
            Closure around urwid.CheckBox.get_state(), which we'll
            use to scrape the value out when we're all done.
            """
            return field_widget.get_state()
        fieldmgr.set_getter(fld_name, getter)
        fieldmgr.set_required_checker(fld_name, is_required)
        fieldmgr.set_label_getter(fld_name, get_label)

    field_widget = urwid.AttrWrap(field_widget, 'field', 'fieldfocus')

    # put everything together.  Each column is either 'fixed' for a fixed width,
    # or given a 'weight' to help determine the relative width of the column
    # such that it can fill the row.
    editwidget = urwid.Columns([
                                ('weight', 1, label),
                                ('fixed',  2, colon),
                                ('weight', 2, field_widget)])

    wrapper = urwid.AttrWrap(editwidget, None, {'label':'labelfocus'})
    return urwid.Padding(wrapper, ('fixed left', 3), ('fixed right', 3))


def form_ok_handler(extra_args, handler, button):
    fieldmgr = extra_args
    dict_values = fieldmgr.get_value_dict()
    if dict_values is not None:
        handler(dict_values)


def form_button(caption, callback, fieldmgr):
    button = urwid.Button(caption)
    urwid.connect_signal(button, 'click', form_ok_handler,
                         user_args=[fieldmgr, callback])
    return urwid.AttrMap(button, None, focus_map='reversed')


def menu_button(caption, callback):
    if callback == not_implemented:
        caption = caption + ' (NI)'
    button = urwid.Button(caption)
    urwid.connect_signal(button, 'click', callback)
    btn_attr_map = None
    btn_focus_map = 'reversed'

    return urwid.AttrMap(button, btn_attr_map, focus_map=btn_focus_map)


def sub_menu(caption, choices):
    contents = menu(caption, choices)
    def open_menu(button):
        return top.open_box(contents)
    return menu_button([caption, u'...'], open_menu)


def menu(title, choices):
    body = [urwid.Text(title), urwid.Divider()]
    body.extend(choices)
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))


def not_implemented(button):
    message_box("Not yet implemented")


def run_form(form_title, fields, on_ok_handler):
    global field_mgr
    title = urwid.Text(form_title)
    form_widgets = [title, urwid.Divider(bottom=2)]
    field_mgr = FieldManager()

    for field_def in fields:
        form_widgets.append(get_field(field_def, field_mgr))

    form_widgets.append(urwid.Divider())
    ok = form_button(UI_TEXT_OK, on_ok_handler, field_mgr)
    form_widgets.append(ok)
    listbox = urwid.Pile(form_widgets)
    #listbox = urwid.ListBox(urwid.SimpleFocusListWalker(form_widgets))
    top.open_box(urwid.Filler(listbox))


def run_command(cmd, title=None):
    show_running_box(title)
    results = commands.getstatusoutput(cmd)
    hide_running_box()
    return results


def show_running_box(title=None):
    cur_time = time.time()
    ts_format = '%Y-%m-%d %H:%M:%S'
    sys_time_text = "(started: %s)" % datetime.datetime.fromtimestamp(cur_time).strftime(ts_format)

    list_widgets = []
    if title is not None and len(title) > 0:
        title = " %s %s" % (title, sys_time_text)
    else:
        title = " %s" % sys_time_text

    list_widgets.append(urwid.Text([title, u'\n', u'\n']))

    list_widgets.append(urwid.Text([" Running ...", u'\n']))
    top.open_box(urwid.Filler(urwid.Pile(list_widgets)))
    mainloop.draw_screen()


def hide_running_box():
    close_box(None)
    mainloop.draw_screen()


def message_box(message_text):
    text_widget = urwid.Text([message_text, u'\n'])
    ok_button = menu_button(UI_TEXT_OK, close_box)
    top.open_box(urwid.Filler(urwid.Pile([text_widget, ok_button])))


def program_about(button):
    about_string = "%s\n%s %s" % (PROGRAM_NAME, LBL_VERSION, PROGRAM_VERSION)
    message_box(about_string)


def program_sys_info(button):
    sys_info_string = ''

    if sys.platform == 'linux2':
        # this might not be the best way to do this
        if os.path.isfile('/etc/lsb-release'):
            cmd = "cat /etc/lsb-release | grep DISTRIB_DESCRIPTION | cut -f 2 -d '=' | cut -f 2 -d '\"'"
            rc, output = commands.getstatusoutput(cmd)
            if rc == 0 and len(output) > 0:
                sys_info_string = output

    if len(sys_info_string) > 0:
        message_box(sys_info_string)
    else:
        message_box("System information not available")


def program_python_info(button):
    v = sys.version_info
    version_string = "Python %d.%d.%d %s" % (v.major,v.minor,v.micro,v.releaselevel)
    message_box(version_string)


def program_quit(button):
    raise urwid.ExitMainLoop()


def obj_stor_devices(button):
    pass


def obj_stor_logs(button):
    pass


def obj_stor_middleware(button):
    pass


def obj_stor_recon(button):
    pass


def obj_stor_rings(button):
    pass


def obj_stor_security(button):
    pass


def obj_stor_status(button):
    pass


def obj_stor_s3(button):
    pass


def example_form(button):
    cmd = "some_command.sh %s %s" % ("arg1", "arg2")
    rc, output = run_command(cmd, "Some Command")
    if rc == 0 and len(output) > 0:
        result_lines = []
        for output_line in output_lines:
            result_lines.append(output_line)

        if len(result_lines) == 0:
            result_lines.append("No output")
        else:
            result_lines.append('\n')
            result_lines.append("Command completed successfully")

        display_output_lines("Command Result", result_lines)
    else:
        message_box("Unable to run command")


title_string = "%s (v%s)" % (PROGRAM_NAME,PROGRAM_VERSION)

menu_top = menu(title_string, [
    sub_menu(MNU_PROGRAM, [
        menu_button(MNU_PROG_ABOUT,            program_about),
        menu_button(MNU_PROG_SYS_INFO,         program_sys_info),
        menu_button(MNU_PROG_PYTHON_INFO,      program_python_info)
    ]),
    sub_menu(MNU_CLUSTER_ADMIN, [
        menu_button(MNU_CLSTR_DEFINE,          not_implemented),
        menu_button(MNU_CLSTR_OPEN,            not_implemented),
        menu_button(MNU_CLSTR_CLOSE,           not_implemented),
        menu_button(MNU_CLSTR_HEALTH,          not_implemented),
        menu_button(MNU_CLSTR_PING,            not_implemented),
        menu_button(MNU_CLSTR_UPTIME,          not_implemented),
        menu_button(MNU_CLSTR_LOAD_AVG,        not_implemented),
        menu_button(MNU_CLSTR_OS,              not_implemented),
        menu_button(MNU_CLSTR_HW_REPORT,       not_implemented)
    ]),
    sub_menu(MNU_SERVERS, [
        menu_button(MNU_SRV_CPUS,              not_implemented),
        menu_button(MNU_SRV_DISKS,             not_implemented),
        menu_button(MNU_SRV_FILESYSTEMS,       not_implemented),
        menu_button(MNU_SRV_LOGS,              not_implemented),
        menu_button(MNU_SRV_MEMORY,            not_implemented),
        menu_button(MNU_SRV_NET_INTERFACES,    not_implemented),
        menu_button(MNU_SRV_OS,                not_implemented),
        menu_button(MNU_SRV_PACKAGES,          not_implemented),
        menu_button(MNU_SRV_PROCESSES,         not_implemented),
        menu_button(MNU_SRV_USERS,             not_implemented)
    ]),
    sub_menu(MNU_BLOCK_STORAGE, [
        menu_button(MNU_BLK_STOR_HEALTH,       not_implemented),
        menu_button(MNU_BLK_STOR_VOLUMES,      not_implemented),
        menu_button(MNU_BLK_STOR_ATTACHMENTS,  not_implemented),
        menu_button(MNU_BLK_STOR_SNAPSHOTS,    not_implemented),
        menu_button(MNU_BLK_STOR_IMAGES,       not_implemented),
        menu_button(MNU_BLK_STOR_PLUGINS,      not_implemented)
    ]),
    sub_menu(MNU_CEPH, [
        menu_button(MNU_CEPH_HEALTH,           not_implemented),
        menu_button(MNU_CEPH_MON,              not_implemented),
        menu_button(MNU_CEPH_OSD,              not_implemented),
        menu_button(MNU_CEPH_POOLS,            not_implemented),
        menu_button(MNU_CEPH_RGW,              not_implemented),
        menu_button(MNU_CEPH_SECURITY,         not_implemented)
    ]),
    sub_menu(MNU_COMPUTE, [
        menu_button(MNU_COMPUTE_DB,            not_implemented),
        menu_button(MNU_COMPUTE_API,           not_implemented),
        menu_button(MNU_COMPUTE_AUTH,          not_implemented),
        menu_button(MNU_COMPUTE_FLAVORS,       not_implemented),
        menu_button(MNU_COMPUTE_IMAGES,        not_implemented),
        menu_button(MNU_COMPUTE_INSTANCES,     not_implemented)
    ]),
    sub_menu(MNU_DASHBOARD, [
        menu_button(MNU_PLACEHOLDER,           not_implemented),
        menu_button(MNU_PLACEHOLDER,           not_implemented),
        menu_button(MNU_PLACEHOLDER,           not_implemented)
    ]),
    sub_menu(MNU_NETWORK, [
        menu_button(MNU_NET_PLUGINS,           not_implemented),
        menu_button(MNU_NET_AGENTS,            not_implemented),
        menu_button(MNU_NET_PROVIDER_NET,      not_implemented),
        menu_button(MNU_NET_TENANT_NET,        not_implemented),
        menu_button(MNU_NET_NAMESPACES,        not_implemented),
        menu_button(MNU_NET_TRAFFIC,           not_implemented)
    ]),
    sub_menu(MNU_OBJECT_STORAGE, [
        menu_button(MNU_OBJ_STOR_HEALTH,       not_implemented),
        menu_button(MNU_OBJ_STOR_DEVICES,      obj_stor_devices),
        menu_button(MNU_OBJ_STOR_LOGS,         obj_stor_logs),
        menu_button(MNU_OBJ_STOR_PROCESSES,    not_implemented),
        menu_button(MNU_OBJ_STOR_AUDITOR,      not_implemented),
        menu_button(MNU_OBJ_STOR_MIDDLEWARE,   obj_stor_middleware),
        menu_button(MNU_OBJ_STOR_RECON,        obj_stor_recon),
        menu_button(MNU_OBJ_STOR_RINGS,        obj_stor_rings),
        menu_button(MNU_OBJ_STOR_POLICIES,     not_implemented),
        menu_button(MNU_OBJ_STOR_SECURITY,     obj_stor_security),
        menu_button(MNU_OBJ_STOR_STATUS,       obj_stor_status),
        menu_button(MNU_OBJ_STOR_S3,           obj_stor_s3)
    ]),
    sub_menu(MNU_IMAGES, [
        menu_button(MNU_PLACEHOLDER,           not_implemented),
        menu_button(MNU_PLACEHOLDER,           not_implemented),
        menu_button(MNU_PLACEHOLDER,           not_implemented)
    ]),
    sub_menu(MNU_SECURITY, [
        menu_button(MNU_SEC_USERS,             not_implemented),
        menu_button(MNU_SEC_TENANTS,           not_implemented),
        menu_button(MNU_SEC_ROLES,             not_implemented),
        menu_button(MNU_SEC_CREDENTIALS,       not_implemented),
        menu_button(MNU_SEC_AUTHENTICATION,    not_implemented),
        menu_button(MNU_SEC_TOKENS,            not_implemented),
        menu_button(MNU_SEC_SERVICES,          not_implemented),
        menu_button(MNU_SEC_ENDPOINTS,         not_implemented)
    ]),
    sub_menu(MNU_HELP, [
        menu_button(MNU_PLACEHOLDER,           not_implemented),
        menu_button(MNU_PLACEHOLDER,           not_implemented),
        menu_button(MNU_PLACEHOLDER,           not_implemented)
    ]),
    menu_button(MNU_PROG_QUIT,                 program_quit)
])


def run():
    global top
    global mainloop
    top = CascadingBoxes(menu_top)
    mainloop = urwid.MainLoop(top, palette=[('reversed', 'standout', '')])
    mainloop.run()


def main():
    run()


if __name__=='__main__':
    main()

