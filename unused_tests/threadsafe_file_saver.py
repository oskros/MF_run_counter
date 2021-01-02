import concurrent.futures
import json
import os
import atomicwrites
import tempfile


def json_dump1(dest_file, data):
    tmp_file = dest_file[:-5] + '_tmp.json'
    with open(tmp_file, 'w') as fo:
        json.dump(data, fo, indent=2)
        fo.flush()
        os.fsync(fo.fileno())
    try:
        os.replace(tmp_file, dest_file)
    except Exception as e:
        print(f"fail {e} for {data}")
        return False
    return True


def json_dump2(dest_file: str, data: [dict, list]) -> bool:
    with tempfile.NamedTemporaryFile("w", dir=".", delete=False) as fo:
        json.dump(data, fo, indent=2)
        fo.flush()
        os.fsync(fo.fileno())
    try:
        os.replace(fo.name, dest_file)
    except Exception as e:
        print(f"fail {e} for {data}")
        return False
    return True


def json_dump3(dest_file, data):
    try:
        with atomicwrites.atomic_write(dest_file, overwrite=True) as fo:
            json.dump(data, fo, indent=2)
    except Exception as e:
        print(f"fail {e} for {data}")
        return False
    return True


if __name__ == "__main__":

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = {
            executor.submit(json_dump3, "demo.json", {"random": f"data {i}"}): i
            for i in range(5)
        }

        done, _ = concurrent.futures.wait(
            futures, return_when=concurrent.futures.ALL_COMPLETED
        )

        for d in done:
            print(f"{d}: successful: {d.result()}")