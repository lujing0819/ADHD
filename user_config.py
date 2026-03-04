from datetime import date, datetime
from typing import Optional, List, Dict, Literal
from pydantic import BaseModel, Field, field_validator

# -------------------- 嵌套子模型 --------------------
class PersonalInfo(BaseModel):
    """个人信息"""
    nickname: str = Field(..., description="昵称")
    real_name: Optional[str] = Field(None, description="真实姓名（建议加密存储）")
    birth_date: date = Field(..., description="出生日期")
    gender: Literal['male', 'female', 'other'] = Field(..., description="性别")
    profile_photo_url: Optional[str] = Field(None, description="头像URL")

    @field_validator('birth_date')
    def validate_age(cls, v):
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 0 or age > 18:
            raise ValueError('年龄必须在0-18岁之间')
        return v

    @property
    def age(self) -> int:
        """计算当前年龄"""
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

class DiagnosisInfo(BaseModel):
    """诊断信息"""
    diagnosis: str = Field(..., description="诊断名称，如'阿斯伯格综合征'")
    diagnosis_date: Optional[date] = Field(None, description="诊断日期")
    diagnosing_clinician: Optional[str] = Field(None, description="诊断医生/机构")
    severity: Optional[str] = Field(None, description="严重程度（如'轻度'）")
    comorbidities: List[str] = Field(default_factory=list, description="共病，如ADHD、焦虑等")

class Symptoms(BaseModel):
    """症状特征"""
    social_difficulties: bool = Field(False, description="社交困难")
    communication_difficulties: bool = Field(False, description="沟通困难")
    repetitive_behaviors: bool = Field(False, description="重复刻板行为")
    restricted_interests: bool = Field(False, description="兴趣狭窄")
    sensory_sensitivities: bool = Field(False, description="感觉过敏")
    specific_symptoms: List[str] = Field(default_factory=list, description="具体症状列表，如'眼神回避'、'鹦鹉学舌'")

class Interests(BaseModel):
    """兴趣与爱好"""
    special_interests: List[str] = Field(default_factory=list, description="特殊兴趣领域，如'火车'、'恐龙'")
    preferred_topics: List[str] = Field(default_factory=list, description="偏好的对话主题")
    favorite_activities: List[str] = Field(default_factory=list, description="喜欢的活动")
    favorite_toys_games: List[str] = Field(default_factory=list, description="喜欢的玩具/游戏")
    favorite_books_movies: List[str] = Field(default_factory=list, description="喜欢的书籍/电影")

class Communication(BaseModel):
    """沟通偏好"""
    mode: Literal['verbal', 'non_verbal', 'aac', 'mixed'] = Field(..., description="沟通方式：言语、非言语、辅助沟通、混合")
    language_level: Optional[str] = Field(None, description="语言水平描述，如'简单句子'")
    prefers_visual_aids: bool = Field(False, description="是否偏好视觉辅助（如图片、符号）")
    typical_expressions: List[str] = Field(default_factory=list, description="常用表达或短语")
    communication_prompt: Optional[str] = Field(None, description="如何引导沟通，如'使用简单、直接的句子'")

class EmotionalBehavior(BaseModel):
    """情绪与行为"""
    common_emotions: List[str] = Field(default_factory=list, description="常见情绪，如'焦虑'、'兴奋'")
    triggers: List[str] = Field(default_factory=list, description="情绪触发因素")
    calming_strategies: List[str] = Field(default_factory=list, description="安抚策略")
    current_mood: Optional[str] = Field(None, description="当前情绪（动态更新）")
    behavior_patterns: Optional[str] = Field(None, description="行为模式描述，如'摇晃身体'")

class DailyRoutine(BaseModel):
    """日常作息"""
    daily_schedule: Dict[str, str] = Field(default_factory=dict, description="日常作息，如{'起床':'07:00'}")
    important_routines: List[str] = Field(default_factory=list, description="必须遵循的流程，如'睡前故事'")
    transitions_difficulty: bool = Field(False, description="是否难以在不同活动间过渡")

class Caregiver(BaseModel):
    """照顾者信息"""
    name: str = Field(..., description="姓名")
    relationship: str = Field(..., description="关系，如'母亲'、'父亲'")
    contact_info: Optional[str] = Field(None, description="联系方式（建议加密存储）")

class FamilyCaregivers(BaseModel):
    """家庭与照顾者"""
    caregivers: List[Caregiver] = Field(default_factory=list, description="主要照顾者")
    family_members: List[str] = Field(default_factory=list, description="家庭成员关系，如'姐姐'")
    home_environment: Optional[str] = Field(None, description="家庭环境描述")

class MedicalIntervention(BaseModel):
    """医疗干预"""
    type: str = Field(..., description="干预类型，如'行为治疗'、'言语治疗'")
    provider: Optional[str] = Field(None, description="提供者/机构")
    frequency: Optional[str] = Field(None, description="频率，如'每周2次'")
    start_date: Optional[date] = Field(None, description="开始日期")
    notes: Optional[str] = Field(None, description="备注")

class Medication(BaseModel):
    """药物"""
    name: str = Field(..., description="药物名称")
    dosage: str = Field(..., description="剂量")
    schedule: str = Field(..., description="用药时间，如'每日早餐后'")
    prescribed_by: Optional[str] = Field(None, description="开药医生")

class MedicalEducational(BaseModel):
    """医疗与教育"""
    interventions: List[MedicalIntervention] = Field(default_factory=list, description="正在接受的干预")
    medications: List[Medication] = Field(default_factory=list, description="正在使用的药物")
    school_name: Optional[str] = Field(None, description="学校名称")
    grade: Optional[str] = Field(None, description="年级")
    education_plan: Optional[str] = Field(None, description="教育计划，如IEP")
    learning_strengths: List[str] = Field(default_factory=list, description="学习优势，如'视觉记忆强'")
    learning_challenges: List[str] = Field(default_factory=list, description="学习挑战，如'抽象概念理解困难'")

class Social(BaseModel):
    """社交情况"""
    peer_interaction: Optional[str] = Field(None, description="与同龄人互动情况描述")
    friendships: List[str] = Field(default_factory=list, description="朋友姓名或昵称")

class SensoryDetails(BaseModel):
    """感觉过敏详情"""
    auditory_sensitivity: Optional[str] = Field(None, description="听觉敏感，如'怕吹风机声'")
    tactile_sensitivity: Optional[str] = Field(None, description="触觉敏感，如'抵触某些布料'")
    visual_sensitivity: Optional[str] = Field(None, description="视觉敏感，如'怕强光'")
    olfactory_sensitivity: Optional[str] = Field(None, description="嗅觉敏感")
    gustatory_sensitivity: Optional[str] = Field(None, description="味觉敏感")
    proprioceptive_sensitivity: Optional[str] = Field(None, description="本体感觉敏感，如'喜欢被拥抱'")
    vestibular_sensitivity: Optional[str] = Field(None, description="前庭感觉敏感，如'怕荡秋千'")

class SpecialNeeds(BaseModel):
    """特殊需求"""
    sensory_sensitivities: SensoryDetails = Field(default_factory=SensoryDetails, description="感觉过敏详情")
    dietary_restrictions: List[str] = Field(default_factory=list, description="饮食限制")
    allergies: List[str] = Field(default_factory=list, description="过敏")

class DynamicData(BaseModel):
    """动态交互数据"""
    last_interaction: Optional[datetime] = Field(None, description="最后互动时间")
    interaction_history_summary: Optional[str] = Field(None, description="互动历史摘要")
    current_session_data: Optional[Dict] = Field(None, description="当前会话上下文")
    notes: Optional[str] = Field(None, description="备注")

# -------------------- 主模型 --------------------
class ChildUserProfile(BaseModel):
    """儿童阿斯伯格用户画像"""
    user_id: str = Field(..., description="用户唯一标识")
    personal_info: PersonalInfo = Field(..., description="个人信息")
    diagnosis_info: DiagnosisInfo = Field(..., description="诊断信息")
    symptoms: Symptoms = Field(default_factory=Symptoms, description="症状特征")
    interests: Interests = Field(default_factory=Interests, description="兴趣与爱好")
    communication: Communication = Field(..., description="沟通偏好")
    emotional_behavior: EmotionalBehavior = Field(default_factory=EmotionalBehavior, description="情绪行为")
    daily_routine: DailyRoutine = Field(default_factory=DailyRoutine, description="日常作息")
    family_caregivers: FamilyCaregivers = Field(default_factory=FamilyCaregivers, description="家庭与照顾者")
    medical_educational: MedicalEducational = Field(default_factory=MedicalEducational, description="医疗与教育")
    social: Social = Field(default_factory=Social, description="社交情况")
    special_needs: SpecialNeeds = Field(default_factory=SpecialNeeds, description="特殊需求")
    dynamic: DynamicData = Field(default_factory=DynamicData, description="动态数据")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    class Config:
        validate_assignment = True  # 赋值时验证

# -------------------- 使用示例 --------------------
if __name__ == "__main__":
    # 创建用户画像实例
    profile = ChildUserProfile(
        user_id="child_001",
        personal_info=PersonalInfo(
            nickname="小星",
            birth_date=date(2016, 5, 20),
            gender="male"
        ),
        diagnosis_info=DiagnosisInfo(
            diagnosis="阿斯伯格综合征",
            diagnosis_date=date(2020, 3, 15),
            severity="轻度"
        ),
        communication=Communication(
            mode="verbal",
            language_level="简单句子",
            prefers_visual_aids=True,
            typical_expressions=["我要火车", "不喜欢"]
        ),
        interests=Interests(
            special_interests=["火车", "数字"],
            preferred_topics=["火车时刻表", "数字游戏"],
            favorite_activities=["拼图", "看火车视频"]
        ),
        emotional_behavior=EmotionalBehavior(
            common_emotions=["焦虑", "兴奋"],
            triggers=["计划改变", "大声响"],
            calming_strategies=["拥抱", "听安静音乐"]
        )
    )

    # 自动计算年龄
    print(f"年龄: {profile.personal_info.age}")  # 输出：年龄: 8（取决于当前日期）


    # 输出JSON（排除未设置的字段）
    print(profile.model_dump_json(indent=2, exclude_none=True))