import Foundation

func decodeName(from data: Data) -> String {
    let value = try! JSONSerialization.jsonObject(with: data) as! [String: Any]
    return value["name"] as! String
}
