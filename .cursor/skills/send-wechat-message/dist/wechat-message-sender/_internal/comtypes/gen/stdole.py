from enum import IntFlag

import comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0 as __wrapper_module__
from comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0 import (
    COMMETHOD, DISPPROPERTY, FONTITALIC, OLE_XPOS_PIXELS, _lcid,
    IPictureDisp, DISPMETHOD, StdFont, EXCEPINFO, OLE_OPTEXCLUSIVE,
    OLE_COLOR, OLE_XSIZE_CONTAINER, DISPPARAMS, typelib_path,
    OLE_ENABLEDEFAULTBOOL, OLE_YSIZE_HIMETRIC, FONTSIZE, Font,
    OLE_YPOS_CONTAINER, Gray, IEnumVARIANT, IDispatch,
    OLE_YPOS_HIMETRIC, FONTBOLD, VgaColor, _check_version, FontEvents,
    FONTSTRIKETHROUGH, GUID, IFont, OLE_YSIZE_CONTAINER, dispid,
    OLE_XSIZE_HIMETRIC, StdPicture, Picture, Checked, IPicture,
    OLE_XPOS_CONTAINER, OLE_YSIZE_PIXELS, OLE_HANDLE, OLE_CANCELBOOL,
    FONTNAME, Default, CoClass, Color, FONTUNDERSCORE, Unchecked,
    BSTR, VARIANT_BOOL, OLE_XPOS_HIMETRIC, HRESULT, OLE_XSIZE_PIXELS,
    IFontEventsDisp, IUnknown, Library, Monochrome, IFontDisp,
    OLE_YPOS_PIXELS
)


class LoadPictureConstants(IntFlag):
    Default = 0
    Monochrome = 1
    VgaColor = 2
    Color = 4


class OLE_TRISTATE(IntFlag):
    Unchecked = 0
    Checked = 1
    Gray = 2


__all__ = [
    'IFont', 'FONTITALIC', 'OLE_XPOS_PIXELS', 'OLE_YSIZE_CONTAINER',
    'IPictureDisp', 'OLE_XSIZE_HIMETRIC', 'StdFont',
    'OLE_OPTEXCLUSIVE', 'StdPicture', 'OLE_COLOR',
    'OLE_XSIZE_CONTAINER', 'Picture', 'Checked', 'IPicture',
    'typelib_path', 'OLE_ENABLEDEFAULTBOOL', 'OLE_YSIZE_HIMETRIC',
    'OLE_TRISTATE', 'FONTSIZE', 'Font', 'OLE_YPOS_CONTAINER',
    'OLE_XPOS_CONTAINER', 'Gray', 'OLE_YSIZE_PIXELS', 'OLE_HANDLE',
    'OLE_CANCELBOOL', 'FONTNAME', 'LoadPictureConstants', 'Default',
    'OLE_YPOS_HIMETRIC', 'Color', 'VgaColor', 'FONTBOLD',
    'FONTUNDERSCORE', 'Unchecked', 'OLE_XPOS_HIMETRIC',
    'OLE_XSIZE_PIXELS', 'IFontEventsDisp', 'FontEvents',
    'FONTSTRIKETHROUGH', 'Library', 'Monochrome', 'IFontDisp',
    'OLE_YPOS_PIXELS'
]

