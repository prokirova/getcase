const addSkillBtn = document.getElementById("add-skill")
const skillsContainer = document.getElementById("skills-container")

function generateNewSkill() {
    const newSkill = document.createElement("div");
    newSkill.className = "skillbox";
    newSkill.textContent = "NEWSKILL!";
    return newSkill;
}

addSkillBtn.addEventListener("click", () => {
    skillsContainer.insertBefore(generateNewSkill(), addSkillBtn);
})