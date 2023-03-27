function getCookie(cookieName) {
    // var cookiePattern = new RegExp("(^|;)[ ]*" + cookieName + "=([^;]*)")
    //   , cookieMatch = cookiePattern.exec(documentAlias.cookie);
    // return cookieMatch ? decodeWrapper(cookieMatch[2]) : 0
    return 0
}

function generateRandomUuid() {
    var d = new Date().getTime();
    d += performance.now()
    var uuid = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function(c) {
        var r = (d + Math.random() * 16) % 16 | 0;
        d = Math.floor(d / 16);
        return (c == "x" ? r : (r & 3 | 8)).toString(16)
    });
    return uuid
}
function loadVisitorIdCookie() {
    var now = new Date(), nowTs = Math.round(now.getTime() / 1000), visitorIdCookieName = '_pk_id', id = getCookie(visitorIdCookieName), cookieValue, uuid;
    if (id) {
        cookieValue = id.split(".");
        cookieValue.unshift("0");
        if (visitorUUID.length) {
            cookieValue[1] = visitorUUID
        }
        return cookieValue
    }

    uuid = generateRandomUuid()
    cookieValue = ["1", uuid, nowTs, 0, nowTs, "", ""];
    return cookieValue
}
function getValuesFromVisitorIdCookie() {
    var cookieVisitorIdValue = loadVisitorIdCookie()
      , newVisitor = cookieVisitorIdValue[0]
      , uuid = cookieVisitorIdValue[1]
      , createTs = cookieVisitorIdValue[2]
      , visitCount = cookieVisitorIdValue[3]
      , currentVisitTs = cookieVisitorIdValue[4]
      , lastVisitTs = cookieVisitorIdValue[5];
    var lastEcommerceOrderTs = cookieVisitorIdValue[6];
    return {
        newVisitor: newVisitor,
        uuid: uuid,
        createTs: createTs,
        visitCount: visitCount,
        currentVisitTs: currentVisitTs,
        lastVisitTs: lastVisitTs,
        lastEcommerceOrderTs: lastEcommerceOrderTs
    }
}
var configVisitorCookieTimeout = 33955200000;
function getRemainingVisitorCookieTimeout() {
    var now = new Date()
      , nowTs = now.getTime()
      , cookieCreatedTs = getValuesFromVisitorIdCookie().createTs;
    var createTs = parseInt(cookieCreatedTs, 10);
    var originalTimeout = (createTs * 1000) + configVisitorCookieTimeout - nowTs;
    console.log(originalTimeout)
    return originalTimeout
}
function get_cookie() {
    visitorIdCookieValues = undefined;
    var now = new Date()
      , nowTs = Math.round(now.getTime() / 1000);

        visitorIdCookieValues = getValuesFromVisitorIdCookie()

    var cookieValue = visitorIdCookieValues.uuid + "." + visitorIdCookieValues.createTs + "." + visitorIdCookieValues.visitCount + "." + nowTs + "." + visitorIdCookieValues.lastVisitTs + "." + visitorIdCookieValues.lastEcommerceOrderTs;
    // setCookie(getCookieName("id"), cookieValue, getRemainingVisitorCookieTimeout(), configCookiePath, configCookieDomain)
    console.log(cookieValue);
    getRemainingVisitorCookieTimeout()
    console.log(cookieValue);
    return cookieValue
}

// data = undefined
// setVisitorIdCookie()
get_cookie()