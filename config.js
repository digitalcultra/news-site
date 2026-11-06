// ===== Digital Cultra monetization config (News) =====
// Digital Cultra News Insider (Payhip membership rx0Sb) — paid plans, never "free"
window.MEMBERSHIP_PAGE = "https://payhip.com/b/rx0Sb";
window.MEMBERSHIP_LINKS = {
  monthly: "https://payhip.com/order?link=rx0Sb&pricing_plan=63Wd1yX9zw", // $4/mo
  yearly:  "https://payhip.com/order?link=rx0Sb&pricing_plan=ZwzKa405G9"  // $36/yr
};
window.STORE_URL = "https://payhip.com/DigitalCultra";

// Live Payhip products verified from payhip.com/DigitalCultra (and Illinois kit page).
// NEVER invent /b/ slugs — unknown state kits fall back to STORE_URL.
window.PAYHIP = {
  resetYears: {name:"The Reset Years: Ultimate Survival Guide", icon:"📘", note:"Printable survival guide for uncertain years.", url:"https://payhip.com/b/2FRZT", price:"$9.99"},
  debtFree:   {name:"Debt Free Blueprint", icon:"💸", note:"Snowball & avalanche payoff planner + trackers.", url:"https://payhip.com/b/SFugO", price:"$5.99"},
  bookkeeping:{name:"Side Hustle Bookkeeping Kit", icon:"📒", note:"Income, expense, mileage & quarterly tax tracker.", url:"https://payhip.com/b/XOWjb", price:"$9.99"},
  getHired:   {name:"Get Hired: 2027 Job Search Playbook", icon:"💼", note:"Resume formulas, scripts, interview prep & trackers.", url:"https://payhip.com/b/2WvdE", price:"$11.99"},
  caregiver:  {name:"The Caregiver's Organizer", icon:"🩺", note:"Medication log, medical binder & care planner.", url:"https://payhip.com/b/D2ihq", price:"$7.99"},
  mealPlan:   {name:"Meal Plan Made Simple", icon:"🍽️", note:"Weekly menus, grocery lists & food-safety guide.", url:"https://payhip.com/b/vHSPc", price:"$4.99"},
  focus:      {name:"The Focus Planner", icon:"🎯", note:"90-day undated planner with habit & goal systems.", url:"https://payhip.com/b/mroS5", price:"$7.99"},
  homeschool: {name:"The Homeschool Planner", icon:"📚", note:"Undated planner & record keeper (up to 4 kids).", url:"https://payhip.com/b/ayXVT", price:"$7.99"},
  fitness:    {name:"The 12-Week Fitness Tracker", icon:"🏃", note:"Beginner workout plan & printable log.", url:"https://payhip.com/b/SnvPp", price:"$5.99"},
  wedding:    {name:"The Complete Wedding Planner 2027", icon:"💍", note:"Research-backed guide + 22 printable worksheets.", url:"https://payhip.com/b/vmy9e", price:"$9.99"},
  kindergarten:{name:"Ready for Kindergarten!", icon:"✏️", note:"Parent guide + 60+ printable activity pages.", url:"https://payhip.com/b/XIk2G", price:"$3.99"}
};

// State Family Emergency Safety Kits with verified Payhip /b/ URLs only.
// Codes match profile.state (USPS). Missing states → STORE_URL (never a guessed slug).
window.STATE_KITS = {
  IL: {name:"Illinois Family Emergency Safety Kit", url:"https://payhip.com/b/YWe8q"},
  VA: {name:"Virginia Family Emergency Safety Kit", url:"https://payhip.com/b/aLdKc"},
  WA: {name:"Washington Family Emergency Safety Kit", url:"https://payhip.com/b/mk0PU"},
  WV: {name:"West Virginia Family Emergency Safety Kit", url:"https://payhip.com/b/krVFt"},
  WI: {name:"Wisconsin Family Emergency Safety Kit", url:"https://payhip.com/b/um1B3"},
  WY: {name:"Wyoming Family Emergency Safety Kit", url:"https://payhip.com/b/0dRSo"}
};
window.stateKit = function(st){
  const k = window.STATE_KITS[(st||"").toUpperCase()];
  if(k) return {name:k.name, icon:"🛡️", note:"State-specific 2027 family emergency workbook.", url:k.url, price:"$5", matched:true};
  const label = (st||"Your state") + " Family Emergency Safety Kit";
  return {name:label, icon:"🛡️", note:"All 50 state kits live in the Digital Cultra store.", url:window.STORE_URL, price:"$5", matched:false};
};

// Product listings order for #gear (survival/emergency guides first).
window.GUIDES_FEATURED = ["resetYears","stateKit","debtFree","bookkeeping","getHired","caregiver","mealPlan","focus","homeschool","fitness","wedding","kindergarten"];
window.AFFILIATE = null; // legacy Amazon affiliate removed — money goes to Payhip checkouts
window.FTC_DISCLOSURE = "Digital downloads sold by Digital Cultra on Payhip. Instant PDF delivery after checkout.";
window.MEMBER_KEY = "dcn_member";
