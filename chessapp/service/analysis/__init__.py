from chessapp.service.analysis.analysis import AnalysisService


s_analysis_service_instance: AnalysisService = None


def get_analysis_service() -> AnalysisService:
    global s_analysis_service_instance
    if s_analysis_service_instance is None:
        s_analysis_service_instance = AnalysisService()
    return s_analysis_service_instance
