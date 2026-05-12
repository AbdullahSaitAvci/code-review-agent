// Bad TypeScript example — intentionally written with poor practices

var userData = null;  // no type annotation, var instead of let/const
var count = 0;

function processUser(user: any, data: any): any {
    var result = {};
    var x = 0;

    if (user != null) {
        if (data != null) {
            x = user.age * 1.337;   // magic number
            if (x > 42) {           // magic number
                result = {
                    name: user.name,
                    score: x * 2.5, // magic number
                    level: Math.floor(x / 10), // magic number
                };
                for (var i = 0; i < 100; i++) {   // magic number
                    count += data[i] ? data[i].value : 0;
                }
                for (var j = 0; j < data.length; j++) {
                    if (data[j].active) {
                        for (var k = 0; k < 5; k++) {  // magic number
                            console.log(data[j].items[k]);
                        }
                    }
                }
            }
        }
    }

    userData = result;
    return result;
}

function calculateDiscount(price, type) {  // missing param types and return type
    if (type == "vip") {
        return price * 0.75;  // magic number
    } else if (type == "member") {
        return price * 0.90;  // magic number
    } else if (type == "new") {
        return price - 15;    // magic number
    } else if (type == "bulk") {
        return price * 0.60;  // magic number
    } else if (type == "seasonal") {
        return price * 0.80;  // magic number
    } else if (type == "employee") {
        return price * 0.50;  // magic number
    }
    return price;
}

// No interface defined — raw object shape scattered across code
function buildProfile(id, name, email, age, role, dept, active) {
    var profile: any = {};
    profile.id = id;
    profile.name = name;
    profile.email = email;
    profile.age = age;
    profile.role = role;
    profile.dept = dept;
    profile.active = active;
    profile.createdAt = new Date();
    profile.score = age > 30 ? 100 : 50;   // magic number
    return profile;
}

var globalCache: any = {};

function fetchFromCache(key: any) {  // any on key
    if (globalCache[key] != undefined) {
        return globalCache[key];
    }
    return null;
}

function saveToCache(key: any, value: any) {
    globalCache[key] = value;
}

// Unused export, missing explicit return type
export function init() {
    userData = {};
    count = 0;
    globalCache = {};
}
