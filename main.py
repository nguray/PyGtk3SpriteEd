import sys
import math

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gio, Gtk, Gdk, GdkPixbuf
import cairo
from string import *

from editArea import EditArea, ToolsMode
from colorsBar import ColorsBar
from spritesBar import SpritesBar

TARGET_TYPE_URI_LIST = 80
(TARGET_ENTRY_TEXT, TARGET_ENTRY_PIXBUF) = range(2)
#dnd_list = [ Gtk.TargetEntry( 'text/uri-list', 0, TARGET_TYPE_URI_LIST ) ]

class Application(Gtk.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            application_id="org.example.myapp",
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
            **kwargs
        )
        self.window = None
        self.idTimer = 0
        self.dum = 0

    def on_menu_do_nothing(self, action, param1, param2):
        print("A do nothing menu item was selected.")

    def on_menu_file_new(self, action, param1, param2):
        print("A File|New menu item was selected.")

        dialog = Gtk.Dialog("New Sprite",transient_for=self.window)
        dialog.add_buttons("OK",Gtk.ResponseType.OK,"Cancel",Gtk.ResponseType.CANCEL)
        #dialog.add_button("Cancel",Gtk.ResponseType.CANCEL)

        hbox1 = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 2)
        width_entry = Gtk.Entry.new()
        width_entry.set_text("32")
        width_entry.set_width_chars(6)
        width_entry.set_alignment(0.5)
        width_label = Gtk.Label.new("Width : ")
        hbox1.pack_start(width_label, True, True, 4)
        hbox1.pack_end(width_entry, False, True, 4)
        hbox2 = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 2)
        height_entry = Gtk.Entry.new()
        height_entry.set_text("32")
        height_entry.set_width_chars(6)
        height_entry.set_alignment(0.5)
        height_label = Gtk.Label.new("Height : ")
        hbox2.pack_start(height_label, True, True, 4)
        hbox2.pack_end(height_entry, False, True, 4)

        vbox = dialog.get_content_area()
        vbox.pack_start(hbox1, True, True, 4)
        vbox.pack_start(hbox2, True, True, 4)

        vbox.show_all()

        response = dialog.run()
        if response==Gtk.ResponseType.OK:
            iWidth = int(width_entry.get_text())
            iHeight = int(height_entry.get_text())
            self.mySpritesBar.new_current_sprite( iWidth, iHeight)
        elif response==Gtk.ResponseType.CANCEL:
            pass

        dialog.destroy()

    def on_menu_file_open(self, action, param1, param2):
        print("A File|Open menu item was selected.")
        chooser = Gtk.FileChooserDialog(transient_for=self.window, 
                                        title="Open PNG File",
                                        action=Gtk.FileChooserAction.OPEN)
        chooser.set_default_response(Gtk.ResponseType.OK)
        chooser.add_buttons("Cancel",Gtk.ResponseType.CANCEL)
        chooser.add_buttons("Open",Gtk.ResponseType.OK)
        filter = Gtk.FileFilter()
        filter.set_name("PNG files")
        filter.add_pattern("*.png")
        chooser.add_filter(filter)
        filter = Gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        chooser.add_filter(filter)
        if chooser.run() == Gtk.ResponseType.OK:
            fileName = chooser.get_filename()
            chooser.destroy()
            print(fileName)
            self.mySpritesBar.load_current_sprite(fileName)
        else:
            chooser.destroy()

    def on_menu_file_save(self, action, param1, param2):
        print("A File|Save menu item was selected.")
        sprite = self.mySpritesBar.get_current_sprite()
        if sprite.fileName=="":
            self.on_menu_file_save_as(action, param1, param2)
        else:
            self.mySpritesBar.save_current_sprite(sprite.fileName)

    def on_menu_file_save_as(self, action, param1, param2):
        print("A File|Save As... menu item was selected.")
        chooser = Gtk.FileChooserDialog(transient_for=self.window, 
                                        title="Save PNG File",
                                        action=Gtk.FileChooserAction.SAVE)
        chooser.set_default_response(Gtk.ResponseType.OK)
        chooser.add_buttons("Cancel",Gtk.ResponseType.CANCEL)
        chooser.add_buttons("Save",Gtk.ResponseType.OK)
        filter = Gtk.FileFilter()
        filter.set_name("PNG files")
        filter.add_pattern("*.png")
        chooser.add_filter(filter)
        filter = Gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        chooser.add_filter(filter)
        if chooser.run() == Gtk.ResponseType.OK:
            fileName = chooser.get_filename()
            chooser.destroy()
            if not fileName.endswith(".png"):
                fileName += ".png" 
            print(fileName)
            self.mySpritesBar.save_current_sprite(fileName)
        else:
            chooser.destroy()

    def on_menu_file_quit(self, action, param1, param2):
        self.quit()

    def on_menu_about(self, action, param1, param2):
        about = Gtk.AboutDialog(transient_for=self.window, modal=True)
        about.set_program_name("SpriteEditor")
        about.set_version("0.2")
        about.set_copyright("(c) Raymond NGUYEN THANH")
        about.set_comments("Small Sprite Editor")
        about.set_website("http://www.corsair.com")
        about.set_logo(GdkPixbuf.Pixbuf.new_from_file("res/FloodFillIcon.png"))
        about.run()
        about.destroy()

    def on_menu_edit_undo(self, action, param1, param2):
        self.myEditArea.undo()

    def on_menu_edit_copy(self, action, param1, param2):
        self.myEditArea.copy_select()

    def on_menu_edit_paste(self, action, param1, param2):
        self.myEditArea.paste_copy()

    def on_select_mode(self, action, param1, param2):
        self.currentBtn.set_icon_name("SelectBoxIcon")
        self.myEditArea.set_tool(ToolsMode.SELECT)

    def on_pencil_mode(self, action, param1, param2):
        self.currentBtn.set_icon_name("PencilIcon")
        self.myEditArea.set_tool(ToolsMode.PENCIL)

    def on_rectangle_mode(self, action, param1, param2):
        self.currentBtn.set_icon_name("RectangleIcon")
        self.myEditArea.set_tool(ToolsMode.RECTANGLE)

    def on_ellipse_mode(self, action, param1, param2):
        self.currentBtn.set_icon_name("EllipseIcon")
        self.myEditArea.set_tool(ToolsMode.ELLIPSE)

    def on_fill_mode(self, action, param1, param2):
        self.currentBtn.set_icon_name("FloodFillIcon")
        self.myEditArea.set_tool(ToolsMode.FILL)

    def on_menu_edit_cut(self, action, param1, param2):
        self.myEditArea.cut_select()

    def on_sprite_change(self, sender, crSurface):
        #n1 = sys.getrefcount(crSurface)
        self.myEditArea.set_sprite(crSurface)
        #n2 = sys.getrefcount(crSurface)

    def on_color_sel_dialog_response(self, dialog, result):
        if result == Gtk.ResponseType.OK:
            colorsel = dialog.get_color_selection()
            col = colorsel.get_current_color()
            print(col.to_string())
            rgba = colorsel.get_current_rgba()
            self.myColorsBar.set_color_cell(self.idCell,int(255*rgba.red),int(255*rgba.green),int(255*rgba.blue),255)
            #alpha = dialog.get_current_alpha()
            #color = dialog.get_current_color()
        dialog.destroy()

    def on_choose_color_dialog(self, sender, idCell):
        self.idCell = idCell
        color_sel_dialog = Gtk.ColorSelectionDialog(title="Choose Color",parent=self.window,modal=True) 
        color_sel_dialog.connect("response",self.on_color_sel_dialog_response)
        color_sel_dialog.show_all()

    def on_edit_area_sprite_transform(self, sender, crSurface):
        sprite = self.mySpritesBar.get_current_sprite()
        sprite.surface = crSurface
        self.mySpritesBar.refresh_display()

    def on_edit_area_pick_color(self, sender, a, r, g, b):
        self.myColorsBar.set_foreground_color( a, r, g, b)

    def on_play_mode(self, action, param1, param2):
        nameIcon = self.playBtn.get_icon_name()
        if nameIcon == "PlayToolIcon":
            self.playBtn.set_icon_name("PauseToolIcon")
            self.mySpritesBar.play_sequence()
        else:
            self.playBtn.set_icon_name("PlayToolIcon")
            self.mySpritesBar.stop_sequence()

    def on_menu_image_flip_horizontaly(self, action, param1, param2):
        self.myEditArea.flip_horizontaly()

    def on_menu_image_flip_verticaly(self, action, param1, param2):
        self.myEditArea.flip_verticaly()

    def on_menu_image_swing_left(self, action, param1, param2):
        self.myEditArea.swing_90_left()

    def on_menu_image_swing_right(self, action, param1, param2):
        self.myEditArea.swing_90_right()

    def on_drag_data_received(self, widget, drag_context, x, y, selection, info, time):
        if info == TARGET_TYPE_URI_LIST:
            uris = selection.get_uris()
            filepathname, host = GLib.filename_from_uri(uris[0])
            if filepathname.endswith('.png'):
                print ("path to open {}".format(filepathname))
                self.mySpritesBar.load_current_sprite(filepathname)

    def do_startup(self):
        Gtk.Application.do_startup(self)

        # action = Gio.SimpleAction.new("about", None)
        # action.connect("activate", self.on_about)
        # self.add_action(action)

        # action = Gio.SimpleAction.new("quit", None)
        # action.connect("activate", self.on_quit)
        # self.add_action(action)

    def do_activate(self):
        # We only allow a single window and raise any existing ones
        if not self.window:
            # Windows are associated with the application
            # when the last one is closed the application shuts down

            iconTheme = Gtk.IconTheme.get_default()
            iconTheme.append_search_path("res")

            builder = Gtk.Builder()
            builder.add_from_file("gtkspriteed.glade")
            self.window = builder.get_object("spriteedwin")
            self.window.set_default_size(700, 700)
            self.window.set_position(Gtk.WindowPosition.CENTER)

            self.window.connect('drag_data_received', self.on_drag_data_received)
            targets = Gtk.TargetList.new()
            self.window.drag_dest_set( Gtk.DestDefaults.ALL, \
                            [Gtk.TargetEntry.new('text/uri-list', 0, TARGET_TYPE_URI_LIST)], \
                            Gdk.DragAction.COPY)

            vbox = builder.get_object("vbox")

            self.playBtn = builder.get_object("PlayTool")
            self.currentBtn = builder.get_object("CurrentTool")

            self.mySpritesBar = SpritesBar()
            self.myEditArea = EditArea()
            hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 2)
            hbox.pack_start(self.myEditArea, True, True, 4)
            hbox.pack_end(self.mySpritesBar, False, True, 4)

            vbox.pack_start(hbox, True, True, 2)
            self.myColorsBar = ColorsBar()
            vbox.pack_start(self.myColorsBar, False, True, 4)

            sprite = self.mySpritesBar.get_current_sprite()
            self.myEditArea.set_sprite(sprite.surface)

            self.myEditArea.set_tool(ToolsMode.PENCIL)

            # Créer un groupe d'actions
            action_group = Gio.SimpleActionGroup()

            # Ajouter les actions par un tuple
            action_group.add_action_entries(
                [
                    ("new", self.on_menu_file_new),
                    ("quit", self.on_menu_file_quit),
                    ("open", self.on_menu_file_open),
                    ("save", self.on_menu_file_save),
                    ("saveas", self.on_menu_file_save_as),
                    ("undo", self.on_menu_edit_undo),
                    ("copy", self.on_menu_edit_copy),
                    ("paste", self.on_menu_edit_paste),
                    ("cut", self.on_menu_edit_cut),
                    ("about", self.on_menu_about),
                    ("selectmode", self.on_select_mode),
                    ("pencilmode", self.on_pencil_mode),
                    ("rectanglemode", self.on_rectangle_mode),
                    ("ellipsemode", self.on_ellipse_mode),
                    ("fillmode", self.on_fill_mode),
                    ("playmode", self.on_play_mode),
                    ("flip_horizontaly", self.on_menu_image_flip_horizontaly),
                    ("flip_verticaly", self.on_menu_image_flip_verticaly),
                    ("swing_right", self.on_menu_image_swing_right),
                    ("swing_left", self.on_menu_image_swing_left)                    
                ]
            )

            # Associer le groupe d'actions avec la fenêtre
            self.window.insert_action_group("actions",action_group)

            # Créer un groupe d"accélérateurs
            agr = Gtk.AccelGroup()
            # Associer ce groupe avec la fenêtre
            self.window.add_accel_group(agr)

            #
            edit_copy = builder.get_object("copyItem")
            key, mod = Gtk.accelerator_parse("<Control>C")
            edit_copy.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)
            edit_paste = builder.get_object("pasteItem")
            key, mod = Gtk.accelerator_parse("<Control>V")
            edit_paste.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)
            edit_cut = builder.get_object("cutItem")
            key, mod = Gtk.accelerator_parse("<Control>X")
            edit_cut.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)

            self.window.show_all()
            self.add_window(self.window)

            self.myColorsBar.connect("forecolor_changed", self.myEditArea.set_foreground_color_cb)
            self.myColorsBar.connect("backcolor_changed", self.myEditArea.set_background_color_cb)
            self.myColorsBar.connect("choose_color_dialog", self.on_choose_color_dialog)

            self.myColorsBar.emit_colors_update()

            self.myEditArea.connect("sprite_modified", self.mySpritesBar.on_sprite_modified)
            self.myEditArea.connect("sprite_transform", self.on_edit_area_sprite_transform)
            self.myEditArea.connect("pick_color",self.on_edit_area_pick_color)

            self.mySpritesBar.connect("sprite_change", self.on_sprite_change)

        self.window.present()

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        # convert GVariantDict -> GVariant -> dict
        options = options.end().unpack()

        if "test" in options:
            # This is printed on the main instance
            print("Test argument recieved: %s" % options["test"])

        self.activate()
        return 0

    def do_shutdown(self):
        self.myColorsBar.savePalette()
        Gtk.Application.do_shutdown(self)

    # def on_about(self, action, param):
    #     on_menu_about(self, action, None, None)

    # def on_quit(self, action, param):
    #     self.quit()


if __name__ == "__main__":
    app = Application()
    app.run(sys.argv)
