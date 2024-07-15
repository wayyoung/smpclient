"""Upload a file."""

import argparse
import asyncio
import time
from typing import Final

from smpclient import SMPClient
from smpclient.transport.serial import SMPSerialTransport


async def main() -> None:
    parser = argparse.ArgumentParser(description="Upload an file to an smp server")
    parser.add_argument("port", help="The serial port to connect to")
    parser.add_argument("file_destination", help="The location of the test file")
    args = parser.parse_args()
    port = args.port
    file_destination = args.file_destination

    file_data = b"""Test document
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla est purus, ultrices in porttitor
in, accumsan non quam. Nam consectetur porttitor rhoncus. Curabitur eu est et leo feugiat
auctor vel quis lorem. Ut et ligula dolor, sit amet consequat lorem. Aliquam porta eros sed
velit imperdiet egestas. Maecenas tempus eros ut diam ullamcorper id dictum libero
tempor. Donec quis augue quis magna condimentum lobortis. Quisque imperdiet ipsum vel
magna viverra rutrum. Cras viverra molestie urna, vitae vestibulum turpis varius id.
Vestibulum mollis, arcu iaculis bibendum varius, velit sapien blandit metus, ac posuere lorem
nulla ac dolor. Maecenas urna elit, tincidunt in dapibus nec, vehicula eu dui. Duis lacinia
fringilla massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur
ridiculus mus. Ut consequat ultricies est, non rhoncus mauris congue porta. Vivamus viverra
suscipit felis eget condimentum. Cum sociis natoque penatibus et magnis dis parturient
montes, nascetur ridiculus mus. Integer bibendum sagittis ligula, non faucibus nulla volutpat
vitae. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus.
In aliquet quam et velit bibendum accumsan. Cum sociis natoque penatibus et magnis dis
parturient montes, nascetur ridiculus mus. Vestibulum vitae ipsum nec arcu semper
adipiscing at ac lacus. Praesent id pellentesque orci. Morbi congue viverra nisl nec rhoncus.
Integer mattis, ipsum a tincidunt commodo, lacus arcu elementum elit, at mollis eros ante ac
risus. In volutpat, ante at pretium ultricies, velit magna suscipit enim, aliquet blandit massa
orci nec lorem. Nulla facilisi. Duis eu vehicula arcu. Nulla facilisi. Maecenas pellentesque
volutpat felis, quis tristique ligula luctus vel. Sed nec mi eros. Integer augue enim, sollicitudin
ullamcorper mattis eget, aliquam in est. Morbi sollicitudin libero nec augue dignissim ut
consectetur dui volutpat. Nulla facilisi. Mauris egestas vestibulum neque cursus tincidunt.
Donec sit amet pulvinar orci.
Quisque volutpat pharetra tincidunt. Fusce sapien arcu, molestie eget varius egestas,
faucibus ac urna. Sed at nisi in velit egestas aliquam ut a felis. Aenean malesuada iaculis nisl,
ut tempor lacus egestas consequat. Nam nibh lectus, gravida sed egestas ut, feugiat quis
dolor. Donec eu leo enim, non laoreet ante. Morbi dictum tempor vulputate. Phasellus
ultricies risus vel augue sagittis euismod. Vivamus tincidunt placerat nisi in aliquam. Cras
quis mi ac nunc pretium aliquam. Aenean elementum erat ac metus commodo rhoncus.
Aliquam nulla augue, porta non sagittis quis, accumsan vitae sem. Phasellus id lectus tortor,
eget pulvinar augue. Etiam eget velit ac purus fringilla blandit. Donec odio odio, sagittis sed
iaculis sed, consectetur eget sem. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Maecenas accumsan velit vel turpis rutrum in sodales diam placerat.
Quisque luctus ullamcorper velit sit amet lobortis. Etiam ligula felis, vulputate quis rhoncus
nec, fermentum eget odio. Vivamus vel ipsum ac augue sodales mollis euismod nec tellus.
Fusce et augue rutrum nunc semper vehicula vel semper nisl. Nam laoreet euismod quam at
varius. Sed aliquet auctor nibh. Curabitur malesuada fermentum lacus vel accumsan. Duis
ornare scelerisque nulla, ac pulvinar ligula tempus sit amet. In placerat nulla ac ante
scelerisque posuere. Phasellus at ante felis. Sed hendrerit risus a metus posuere rutrum.
Phasellus eu augue dui. Proin in vestibulum ipsum. Aenean accumsan mollis sapien, ut
eleifend sem blandit at. Vivamus luctus mi eget lorem lobortis pharetra. Phasellus at tortor
quam, a volutpat purus. Etiam sollicitudin arcu vel elit bibendum et imperdiet risus tincidunt.
Etiam elit velit, posuere ut pulvinar ac, condimentum eget justo. Fusce a erat velit. Vivamus
imperdiet ultrices orci in hendrerit.
"""
    async with SMPClient(SMPSerialTransport(), port) as client:
        start_s = time.time()
        async for offset in client.upload_file(
            file_data=file_data, file_destination=file_destination
        ):
            print(
                f"\rUploaded {offset:,} / {len(file_data):,} Bytes | "
                f"{offset / (time.time() - start_s) / 1000:.2f} KB/s           ",
                end="",
                flush=True,
            )
        print()
        print("Finished uploading file")


if __name__ == "__main__":
    asyncio.run(main())
