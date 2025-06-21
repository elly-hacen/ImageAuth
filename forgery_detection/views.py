from django.shortcuts import render
from django.conf import settings
from .forms import ImageUploadForm
from os.path import basename
from .models import User, Image, Metadata, AnalysisResult, UploadLog
import datetime

def home(request):
    from .utils import (
        handle_uploaded_file, convert_to_ela_image,
        predict_image, extract_metadata, noise_analysis_process,
        analyze_histogram, detect_blur, generate_heatmap
    )
    
    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_image = form.cleaned_data["image"]
            saved_path = handle_uploaded_file(uploaded_image)
            saved_name = basename(saved_path)
            entropy_score = analyze_histogram(saved_path)
            blur_score = detect_blur(saved_path)

            ela_img, ela_canny = convert_to_ela_image(saved_path)
            noise_img = noise_analysis_process(saved_path)
            prediction = predict_image(saved_path)
            metadata_dict = extract_metadata(saved_path)
            heatmap_url = generate_heatmap(saved_path)
            

            context = {
                "form": form,
                "original": saved_name,
                "ela_img": ela_img,
                "ela_canny": ela_canny,
                "noise_img": noise_img,
                "prediction": prediction,
                "metadata": metadata_dict,
                "blur_score": round(blur_score, 2),
                "entropy_score": round(entropy_score, 2),
                "MEDIA_URL": settings.MEDIA_URL,
                "heatmap_url": heatmap_url,
            }
            return render(request, "home.html", context)
    else:
        form = ImageUploadForm()

    return render(request, "home.html", {"form": form})
































# def get_client_ip(request):
#     # Helper to get client IP from request headers
#     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#     if x_forwarded_for:
#         ip = x_forwarded_for.split(',')[0]
#     else:
#         ip = request.META.get('REMOTE_ADDR')
#     return ip
            # Save Image record linked to user (assuming logged in)
            # user = request.user if request.user.is_authenticated else None
            # image_obj = Image.objects.create(
            #     filename=saved_name,
            #     user=user,
            #     status="Processed"
            # )

            # # Save Metadata
            # for tag, val in metadata_dict.items():
            #     Metadata.objects.create(
            #         tag=tag,
            #         value=str(val),
            #         image=image_obj
            #     )

            # # Save Analysis Result (dummy confidence as example, adapt as needed)
            # confidence_score = 0.9 if prediction == "Fake" else 0.95
            # AnalysisResult.objects.create(
            #     prediction=prediction,
            #     confidence_score=confidence_score,
            #     image=image_obj
            # )

            # # Log the upload
            # ip = get_client_ip(request)
            # UploadLog.objects.create(
            #     user=user,
            #     image=image_obj,
            #     ip_address=ip
            # )