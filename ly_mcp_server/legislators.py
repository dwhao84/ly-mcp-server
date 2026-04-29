from ly_mcp_server.ly_client import fetch_legislature_dataset


def format_legislator(legislator: dict) -> dict:
    pic_url = legislator.get("picUrl") or ""

    return {
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
    }


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

    return {
        "found": True,
        "legislator": format_legislator(legislator),
    }


async def lookup_legislators_by_party(party: str = "台灣民眾黨") -> dict:
    data = await fetch_legislature_dataset(dataset_id="9", page=1, select_term="all")
    legislators = data.get("jsonList", [])
    normalized_party = party.strip()
    matches = [
        format_legislator(item)
        for item in legislators
        if normalized_party in {item.get("party"), item.get("partyGroup")}
    ]

    return {
        "found": bool(matches),
        "party": normalized_party,
        "count": len(matches),
        "legislators": matches,
        "message": (
            f"找到{len(matches)}位{normalized_party}立法委員。"
            if matches
            else f"找不到{normalized_party}的立法委員資料。"
        ),
    }
