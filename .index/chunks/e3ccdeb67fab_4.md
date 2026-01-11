# Chunk: e3ccdeb67fab_4

- source: `.venv-lab/Lib/site-packages/notebook/static/9250.a4dfe77db702bf7a316c.js`
- lines: 185-261
- chunk: 5/6

```
tri_surf', 'triangulate',
  'trigrid', 'triql', 'trired', 'trisol', 'truncate_lun',
  'ts_coef', 'ts_diff', 'ts_fcast', 'ts_smooth', 'tv',
  'tvcrs', 'tvlct', 'tvrd', 'tvscl', 'typename',
  'uindgen', 'uint', 'uintarr', 'ul64indgen', 'ulindgen',
  'ulon64arr', 'ulonarr', 'ulong', 'ulong64', 'uniq',
  'unsharp_mask', 'usersym', 'value_locate', 'variance', 'vector',
  'vector_field', 'vel', 'velovect', 'vert_t3d', 'voigt',
  'volume', 'voronoi', 'voxel_proj', 'wait', 'warp_tri',
  'watershed', 'wdelete', 'wf_draw', 'where', 'widget_base',
  'widget_button', 'widget_combobox', 'widget_control',
  'widget_displaycontextmenu', 'widget_draw',
  'widget_droplist', 'widget_event', 'widget_info',
  'widget_label', 'widget_list',
  'widget_propertysheet', 'widget_slider', 'widget_tab',
  'widget_table', 'widget_text',
  'widget_tree', 'widget_tree_move', 'widget_window',
  'wiener_filter', 'window',
  'window', 'write_bmp', 'write_csv', 'write_gif', 'write_image',
  'write_jpeg', 'write_jpeg2000', 'write_nrif', 'write_pict', 'write_png',
  'write_ppm', 'write_spr', 'write_srf', 'write_sylk', 'write_tiff',
  'write_video', 'write_wav', 'write_wave', 'writeu', 'wset',
  'wshow', 'wtn', 'wv_applet', 'wv_cwt', 'wv_cw_wavelet',
  'wv_denoise', 'wv_dwt', 'wv_fn_coiflet',
  'wv_fn_daubechies', 'wv_fn_gaussian',
  'wv_fn_haar', 'wv_fn_morlet', 'wv_fn_paul',
  'wv_fn_symlet', 'wv_import_data',
  'wv_import_wavelet', 'wv_plot3d_wps', 'wv_plot_multires',
  'wv_pwt', 'wv_tool_denoise',
  'xbm_edit', 'xdisplayfile', 'xdxf', 'xfont', 'xinteranimate',
  'xloadct', 'xmanager', 'xmng_tmpl', 'xmtool', 'xobjview',
  'xobjview_rotate', 'xobjview_write_image',
  'xpalette', 'xpcolor', 'xplot3d',
  'xregistered', 'xroi', 'xsq_test', 'xsurface', 'xvaredit',
  'xvolume', 'xvolume_rotate', 'xvolume_write_image',
  'xyouts', 'zlib_compress', 'zlib_uncompress', 'zoom', 'zoom_24'
];
var builtins = wordRegexp(builtinArray);

var keywordArray = [
  'begin', 'end', 'endcase', 'endfor',
  'endwhile', 'endif', 'endrep', 'endforeach',
  'break', 'case', 'continue', 'for',
  'foreach', 'goto', 'if', 'then', 'else',
  'repeat', 'until', 'switch', 'while',
  'do', 'pro', 'function'
];
var keywords = wordRegexp(keywordArray);

var identifiers = new RegExp('^[_a-z\xa1-\uffff][_a-z0-9\xa1-\uffff]*', 'i');

var singleOperators = /[+\-*&=<>\/@#~$]/;
var boolOperators = new RegExp('(and|or|eq|lt|le|gt|ge|ne|not)', 'i');

function tokenBase(stream) {
  // whitespaces
  if (stream.eatSpace()) return null;

  // Handle one line Comments
  if (stream.match(';')) {
    stream.skipToEnd();
    return 'comment';
  }

  // Handle Number Literals
  if (stream.match(/^[0-9\.+-]/, false)) {
    if (stream.match(/^[+-]?0x[0-9a-fA-F]+/))
      return 'number';
    if (stream.match(/^[+-]?\d*\.\d+([EeDd][+-]?\d+)?/))
      return 'number';
    if (stream.match(/^[+-]?\d+([EeDd][+-]?\d+)?/))
      return 'number';
  }

  // Handle Strings
  if (stream.match(/^"([^"]|(""))*"/)) { return 'string'; }
```
