from ly_mcp_server.ly_client import fetch_legislature_dataset


async def lookup_legislator_profile(name: str = "黃國昌") -> dict:
    data = await fetch_legislature_dataset(dataset_id="9", page=1, select_term="all")
    legislators = data.get("jsonList", [])
    legislator = next(
        (item for item in legislators if item.get("name") == name),
        None,
    )

    if not legislator:
        return {
            "found": False,
            "name": name,
            "message": f"找不到{name}的立法委員資料。",
        }

    pic_url = legislator.get("picUrl") or ""

    return {
        "found": True,
        "legislator": {
            "found": True,
            "name": legislator.get("name"),
            "ename": legislator.get("ename"),
            "party": legislator.get("party"),
            "partyGroup": legislator.get("partyGroup"),
            "areaName": legislator.get("areaName"),
            "committee": legislator.get("committee"),
            "tel": legislator.get("tel"),
            "fax": legislator.get("fax"),
            "addr": legislator.get("addr"),
            "degree": legislator.get("degree"),
            "experience": legislator.get("experience"),
            "term": legislator.get("term"),
            "onboardDate": legislator.get("onboardDate"),
            "imageUrl": pic_url.replace("http://", "https://"),
        },
    }
