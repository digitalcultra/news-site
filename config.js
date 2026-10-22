// ===== Digital Cultra monetization config (News) =====
// TODO(owner): create these memberships in Payhip (Dashboard > Memberships) and paste the real checkout URLs.
window.MEMBERSHIP_LINKS = {
  monthly: "https://payhip.com/DigitalCultra/TODO-news-member-monthly", // TODO: $4/mo Payhip membership URL
  yearly:  "https://payhip.com/DigitalCultra/TODO-news-member-yearly"   // TODO: $36/yr Payhip membership URL
};
// TODO(owner): replace 'TODO-20' with your Amazon Associates tracking ID (e.g. yourid-20) after approval.
window.AFFILIATE_TAG = "TODO-20";
const _az = q => "https://www.amazon.com/s?k=" + encodeURIComponent(q) + "&tag=" + window.AFFILIATE_TAG;
window.AFFILIATE = {
  gobag:      {name:"Go-bag / 72-hour kit", icon:"🎒", note:"Pre-packed bag for grabbing and going.", url:_az("72 hour emergency go bag")},
  radio:      {name:"NOAA weather radio",   icon:"📻", note:"Hand-crank/battery radio with NOAA alerts.", url:_az("NOAA weather alert radio hand crank")},
  water:      {name:"Water filter",         icon:"💧", note:"Personal or gravity water filter.", url:_az("emergency water filter")},
  power:      {name:"Power bank / solar",   icon:"🔋", note:"Keep phones charged when power is out.", url:_az("solar power bank")},
  firstaid:   {name:"First aid kit",        icon:"🩹", note:"Home and car first aid kits.", url:_az("first aid kit")},
  scanner:    {name:"Police/fire scanner",  icon:"📡", note:"Listen to local public-safety radio.", url:_az("police scanner digital")},
  flashlight: {name:"Flashlight / headlamp",icon:"🔦", note:"LED flashlights, headlamps, batteries.", url:_az("LED flashlight headlamp emergency")},
  generator:  {name:"Generator / power station", icon:"⚡", note:"Portable generators and battery stations.", url:_az("portable power station generator")}
};
window.STORE_URL = "https://payhip.com/DigitalCultra";
window.FTC_DISCLOSURE = "As an Amazon Associate we earn from qualifying purchases.";
// Client-side member flag ONLY (localStorage 'dcn_member'='1'). NOT secure: real gating needs a backend
// that verifies Payhip membership (e.g. Payhip webhook/license check) before serving member content.
window.MEMBER_KEY = "dcn_member";
