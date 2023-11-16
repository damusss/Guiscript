import pygame
import sys
import src.guiscript as guis
import enum

W, H = 450, 850

pygame.init()
screen = pygame.display.set_mode((W, H))
clock = pygame.Clock()

plus = 0.25
minus = -0.25
half = 0.5

GRADE_SIZE = H/10

HIDE_PROFS = False


class Subject(enum.StrEnum):
    science = "science"
    italian = "italian"
    latin = "latin"
    history = "history"
    filosophy = "filosophy"
    math = "math"
    physics = "physics"
    art = "art"
    drawing = "drawing"
    pe = "pe"
    english = "english"


class Mode(enum.StrEnum):
    oral = "oral"
    written = "written"
    practical = "practical"


PROFS = {"CENSORED":"CENSORED"}

GRADES = reversed([
    [7, Subject.drawing, Mode.practical],
    [plus, Subject.drawing, Mode.practical],
    [7+plus, Subject.italian, Mode.written],
    [9+half, Subject.math, Mode.written],
    [8+half, Subject.pe, Mode.practical],
    [9, Subject.english, Mode.oral],
    [9+half, Subject.science, Mode.written],
    [8, Subject.drawing, Mode.practical],
    [8, Subject.art, Mode.oral],
    [8+plus, Subject.italian, Mode.oral],
    [7, Subject.drawing, Mode.practical],
    [8+minus, Subject.latin, Mode.oral]
])


def grade_to_txt(grade):
    if grade == 0.25:
        return "+"
    elif grade == -0.25:
        return "-"
    if int(grade) == grade:
        return grade
    elif grade-int(grade) == 0.25:
        return f"{int(grade)}+"
    elif grade-int(grade) == 0.5:
        return f"{int(grade)} 1/2"
    elif grade-int(grade) == 0.75:
        return f"{int(grade)+1}-"


class Grade:
    def __init__(self, grade, mode, subj):
        self.grade, self.mode, self.subj = grade, mode, subj


GRADE_IDX, SUBJ_IDX, MODE_IDX = 0, 1, 2

GSS = """

.fill_x:: {
    stack.fill_x true;
}

.fill_y:: {
    stack.fill_y true;
}

.fill_all:: {
    stack.fill_x true;
    stack.fill_y true;
}

.big_font:: {
    text.font_size 25;
}

.smol_font:: {
    text.font_size 18;
}

.grade:: {
    shape.enabled true;
    shape.type circle;
    outline.enabled false;
    bg.enabled false;
    stack.fill_y true;
}

.align_left:: {
    stack.align left;
    text.align left;
    text.font_align 0;
}

.good:: {
    shape.color #6fc276;
}

.bad:: {
    shape.color #eb2d3a;
}

.neutral:: {
    shape.color #4285f4;
}

"""
manager = guis.UIManager(screen, gs_sources=[GSS])
main_stack: guis.VStack = None


def calc_average(nums):
    nums = [num.grade for num in nums]
    lennums = len(nums)
    if lennums == 0:
        return -1
    return sum(nums)/lennums


def on_refresh():
    global main_stack
    manager.restart()
    main_stack = generate()


def generate():
    global allcont
    if main_stack is not None:
        main_stack.destroy()

    def on_opt_click(btn: guis.Button):
        for cont, obj in containers.items():
            if cont == btn.text.get_active_text():
                obj.show()
            else:
                obj.hide()

    option_btns = [
        "All",
        "Subject",
    ]

    containers:dict[str, guis.VStack] = {
        "All": None,
        "Subject": None
    }

    prof_grades = {}
    subj_grades = {}
    grades = {"grades": [], "average": -1}
    for grade in GRADES:
        subj = grade[SUBJ_IDX]
        prof = PROFS[subj]
        if not prof in prof_grades:
            prof_grades[prof] = {"grades": [], "average": -1}
        if not subj in subj_grades:
            subj_grades[subj] = {"grades": [], "average": -1}

        grade_obj = Grade(grade[GRADE_IDX], grade[MODE_IDX], grade[SUBJ_IDX])
        subj_grades[subj]["grades"].append(grade_obj)
        prof_grades[prof]["grades"].append(grade_obj)
        grades["grades"].append(grade_obj)

    for prof_grade in list(prof_grades):
        prof_grades[prof_grade]["average"] = calc_average(
            prof_grades[prof_grade]["grades"])
    for subj_grade in list(subj_grades):
        subj_grades[subj_grade]["average"] = calc_average(
            subj_grades[subj_grade]["grades"])
    grades["average"] = calc_average(grades["grades"])

    with guis.VStack(guis.SizeR(W, H)) as main_vstack:
        with guis.HStack(guis.SizeR(0, H/11), style_id="fill_x;invis_cont"):
            for txt in option_btns:
                guis.Button(txt, guis.ZeroR(), style_id="fill_all").status.add_listener(
                    "on_click", on_opt_click)
            guis.Button("Refresh", guis.ZeroR(), style_id="fill_all").status.add_listener(
                "on_click", on_refresh)

        with guis.VStack(guis.ZeroR(), style_id="fill_all"):
            with guis.VStack(guis.ZeroR(), style_id="fill_all;invis_cont") as all_cont:
                for grade in grades["grades"]:
                    ###
                    prof = PROFS[grade.subj]
                    goodbad_style = "good" if grade.grade >= 6 else "bad" if abs(
                        grade.grade) != 0.25 else "neutral"
                    prof_txt = f" | {prof.title()}" if not HIDE_PROFS else ""
                    with guis.HStack(guis.SizeR(0, GRADE_SIZE), style_id="invis_cont;fill_x"):
                        guis.Label(grade_to_txt(grade.grade), guis.SizeR(
                            GRADE_SIZE, 0), style_id=f"grade;{goodbad_style}")
                        with guis.VStack(guis.ZeroR(), style_id="invis_cont;fill_all"):
                            guis.Label(f"{grade.subj.title()}{prof_txt}", guis.SizeR(
                                0, GRADE_SIZE//3), style_id="fill_x;align_left")
                            guis.Label(f"{grade.mode.title()}", guis.SizeR(
                                0, GRADE_SIZE//3), style_id="fill_x;smol_font;align_left")
                    ###

            with guis.VStack(guis.ZeroR(), style_id="fill_all;invis_cont").hide() as subj_cont:
                ...

            containers["All"] = all_cont
            containers["Subject"] = subj_cont
    return main_vstack


main_stack = generate()

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        manager.event(e)

    screen.fill("black")
    
    manager.logic()
    guis.static_logic()
    manager.render()
    
    clock.tick(0)
    pygame.display.update()
    pygame.display.set_caption(f"GRADES {clock.get_fps():.0f} FPS")
