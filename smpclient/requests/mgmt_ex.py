"""The Simple Management Protocol (SMP) header."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict, ValidationInfo, field_validator
from smp import error, header
from smp import image_management as smpimg
from smp import message

GROUP_ID_MGMT_EX = 80

CMD_ID_STATE = 0
CMD_ID_WLC_TX_UPDATE = 1


class MgmtExErrorV1(error.ErrorV1):
    """Image Management error response."""

    _GROUP_ID = GROUP_ID_MGMT_EX


class MgmtExErrorV2(error.ErrorV2[smpimg.IMG_MGMT_ERR]):
    """Image Management error response."""

    _GROUP_ID = GROUP_ID_MGMT_EX


class _MgmtExGroupBase:
    _ErrorV1 = MgmtExErrorV1
    _ErrorV2 = MgmtExErrorV2


class MgmtExStatesReadRequest(message.ReadRequest):
    """Obtain list of images with their current state."""

    _GROUP_ID = GROUP_ID_MGMT_EX
    _COMMAND_ID = CMD_ID_STATE


class MgmtExImageState(BaseModel):
    """The state of an image in a slot."""

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    slot: int
    """Slot number within “image”.

    Each image has two slots:
    - primary (running one) = 0
    - secondary (for DFU dual-bank purposes) = 1.
    """
    version: str
    """Version of the image."""
    image: int | None = None
    """Semi-optional image number.

    The field is not required when only one image is supported by the running
    application.
    """
    hash: smpimg.HashBytes | bytes | None = None
    """SHA256 hash of the image header and body.

    Note that this will not be the same as the SHA256 of the whole file, it is
    the field in the MCUboot TLV section that contains a hash of the data which
    is used for signature verification purposes. This field is optional but only
    optional when using MCUboot's serial recovery feature with one pair of image
    slots, `CONFIG_BOOT_SERIAL_IMG_GRP_HASH` can be disabled to remove
    support for hashes in this configuration. SMP server in applications must
    support sending hashes.
    """
    bootable: bool | None = None
    """True if image has bootable flag set.

    This field does not have to be present if false.
    """
    pending: bool | None = None
    """True if image is set for next swap.

    This field does not have to be present if false.
    """
    confirmed: bool | None = None
    """True if image has been confirmed.

    This field does not have to be present if false.
    """
    active: bool | None = None
    """True if image is currently active application

    This field does not have to be present if false.
    """
    permanent: bool | None = None
    """True if image is to stay in primary slot after the next boot.

    This does not have to be present if false.
    """

    crc: int | None = None
    """CRC
    
    """

    chip: int | None = None
    """Chip model

    """

    @field_validator("hash")
    @classmethod
    def cast_bytes(cls, v: bytes | None, _: ValidationInfo) -> smpimg.HashBytes | None:
        if v is None:
            return None
        return smpimg.HashBytes(v)


class MgmtExStateReadResponse(message.ReadResponse):

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    _GROUP_ID = GROUP_ID_MGMT_EX
    _COMMAND_ID = CMD_ID_STATE

    images: List[MgmtExImageState]
    splitStatus: int | None = None


class MgmtExStatesRead(MgmtExStatesReadRequest, _MgmtExGroupBase):
    _Response = MgmtExStateReadResponse


class MgmtExUpdateWlcTxIcRequest(message.WriteRequest):
    """Update WLC TX IC FW"""

    _GROUP_ID = GROUP_ID_MGMT_EX
    _COMMAND_ID = CMD_ID_WLC_TX_UPDATE


class MgmtExUpdateWlcTxIcResponse(message.WriteResponse):

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    _GROUP_ID = GROUP_ID_MGMT_EX
    _COMMAND_ID = CMD_ID_WLC_TX_UPDATE

    splitStatus: int | None = None


class MgmtExUpdateWlcTxIc(MgmtExUpdateWlcTxIcRequest, _MgmtExGroupBase):
    _Response = MgmtExUpdateWlcTxIcResponse
