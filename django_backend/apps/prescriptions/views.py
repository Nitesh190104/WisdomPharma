from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Prescription
from .serializers import PrescriptionSerializer


class PrescriptionListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        prescriptions = Prescription.objects.filter(user=request.user).order_by('-created_at')
        serializer = PrescriptionSerializer(prescriptions, many=True, context={'request': request})
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Prescriptions retrieved successfully',
        })

    def post(self, request):
        data = request.data.copy()
        serializer = PrescriptionSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                'success': True,
                'data': serializer.data,
                'message': 'Prescription uploaded successfully',
            }, status=201)
        return Response({
            'success': False,
            'data': serializer.errors,
            'message': 'Validation failed',
        }, status=400)
