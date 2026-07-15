# script used to generate ./data/hamlet.rds

data <- data.frame(
    act=1,
    scene=5,
    character=c(
        "",
        "HAMLET",
        "GHOST",
        "HAMLET",
        "GHOST",
        "GHOST",
        "GHOST",
        "HAMLET",
        "GHOST",
        "GHOST",
        "HAMLET"
    ),
    line=c(
        "SCENE V. A more remote part of the Castle.",
        "Whither wilt thou lead me? Speak, I'll go no further.",
        "Mark me.",
        "I will.",
        "My hour is almost come,",
        "When I to sulph'rous and tormenting flames",
        "Must render up myself.",
        "Alas, poor ghost!",
        "Pity me not, but lend thy serious hearing",
        "To what I shall unfold.",
        "Speak, I am bound to hear."
    )
)

save(data, file="data/hamlet.rds")
