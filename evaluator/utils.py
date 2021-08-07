def perf_averager(form):
    efficiency = form.cleaned_data["efficiency"]
    timeliness = form.cleaned_data["timeliness"]
    quality = form.cleaned_data["quality"]
    accuracy = form.cleaned_data["accuracy"]
    return (efficiency + timeliness + quality + accuracy) * 5